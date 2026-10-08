"""Codex-only judging: exclusive execution, durable call logs, no API calls."""
from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

# Reuse frozen serializers/validator/CLI flags. Importing v1 does not load a key
# or call an API; API functions are never used by this module or the v2 runner.
import retrieval_judge_pilot as legacy

ROOT = legacy.ROOT
LOCAL = ROOT / 'knowledge/local'
GLOBAL_LOCK = LOCAL / 'codex-judge.lock'
ACTIVE = LOCAL / 'codex-judge-active.json'
MODEL = 'gpt-6.1-sol'
LABELS = (*legacy.LABELS, 'contradictory')


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value, *, replace=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not replace:
        raise FileExistsError(f'Refusing overwrite: {path.name}')
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


class WorkerBusy(RuntimeError):
    pass


class JudgeLock(AbstractContextManager):
    """Kernel lock releases on process exit; never delete guessed stale locks."""
    def __init__(self, path=GLOBAL_LOCK):
        self.path = path
        self.stream = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open('a+b')
        if self.path.stat().st_size == 0:
            self.stream.write(b'0')
            self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.stream.close()
            self.stream = None
            raise WorkerBusy('Another v2 judge worker holds the lock; no call started') from error
        return self

    def __exit__(self, *args):
        if self.stream is not None:
            self.stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream, fcntl.LOCK_UN)
            self.stream.close()
        return False


def validate(answer, inp, schema):
    errors = legacy.validate_result(answer, inp, schema)
    if errors:
        return errors
    blocks = {b['block']: b['text'] for b in inp['blocks']}
    misleading_quotes = {(e['block'], e['quote']) for f in answer['potentially_misleading'] for e in f['evidence']}
    for finding in answer['contradictory']:
        if not finding['reason'].strip() or not finding['evidence']:
            errors.append('contradiction requires reason and evidence')
        for evidence in finding['evidence']:
            if not evidence['quote'].strip() or evidence['quote'] not in blocks.get(evidence['block'], ''):
                errors.append('contradiction quote absent from stated block')
        if not any((e['block'], e['quote']) in misleading_quotes for e in finding['evidence']):
            errors.append('contradiction must also be potentially misleading with shared evidence')
    return errors


def coverage(answer, inp, expected_result):
    return legacy.coverage(answer, {**inp, 'expected_result': expected_result})


def preflight():
    cli = shutil.which('codex')
    if not cli:
        raise RuntimeError('Codex CLI not found; no substitution')
    env = legacy.codex_environment()
    status = subprocess.run([cli, 'login', 'status'], env=env, capture_output=True,
                            encoding='utf-8', errors='replace', timeout=30)
    if status.returncode or 'Logged in using ChatGPT' not in status.stdout + status.stderr:
        raise RuntimeError('ChatGPT authentication not verified; no API fallback')
    version = subprocess.run([cli, '--version'], env=env, capture_output=True,
                             encoding='utf-8', timeout=30, check=True).stdout.strip()
    cache = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'models_cache.json'
    matches = [m for m in read(cache).get('models', []) if m.get('slug') == MODEL]
    if not matches or not any(e['effort'] == 'medium' for e in matches[0].get('supported_reasoning_levels', [])):
        raise RuntimeError('Exact model / Medium catalog support unavailable; no substitution')
    return {'cli':cli, 'cli_version':version, 'authentication':'chatgpt_subscription',
            'model_requested':MODEL, 'reasoning_effort':'medium', 'catalog_model':matches[0]['slug'],
            'catalog_sha256':legacy.sha(cache), 'server_model_reported':None,
            'server_identity_limit':'JSONL does not expose actual server model/revision'}


def events_and_usage(path):
    events, malformed, usage = [], 0, {}
    if not path.exists():
        return events, malformed, None
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        events.append(event)
        # Account every turn with usage, not only the last successful one.
        for key, value in (event.get('usage') or {}).items():
            if isinstance(value, int):
                usage[key] = usage.get(key, 0) + value
    if usage:
        usage['total_tokens'] = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
    return events, malformed, usage or None


def finalize(run_dir, meta, *, returncode=None, elapsed=None, error=None, recovered=False):
    out = run_dir / 'results' / meta['context_id']
    if (out / 'record.json').exists():
        return read(out / 'record.json')
    intent = read(out / 'intent.json')
    inp = read(run_dir / 'inputs' / (meta['context_id'] + '.json'))
    events, malformed, usage = events_and_usage(out / 'stdout.jsonl')
    complete = any(e.get('type') == 'turn.completed' for e in events)
    messages = [e.get('item', {}).get('text') for e in events
                if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
    tools = [e for e in events if e.get('item', {}).get('type') not in {None,'agent_message','reasoning','error'}]
    errors, answer = [], None
    if tools: errors.append('tool/event isolation violation')
    if malformed: errors.append('malformed JSONL event')
    if returncode not in {None,0}: errors.append('CLI nonzero exit')
    if not complete: errors.append('no completed turn; usage may be unknown')
    if error: errors.append(error)
    try:
        answer = json.loads(messages[-1]) if messages else None
        if answer is None: errors.append('missing final JSON message')
        else: errors += validate(answer, inp, read(run_dir / 'schema.json'))
    except (json.JSONDecodeError, TypeError):
        errors.append('invalid final JSON')
    if answer is not None:
        if (out / 'answer.json').exists():
            if read(out / 'answer.json') != answer:
                raise RuntimeError('Stored answer differs; recovery cannot overwrite it')
        else:
            write(out / 'answer.json', answer)
    record = {**intent, 'finished_at':now(), 'success':not errors, 'validation_errors':errors,
              'returncode':returncode, 'elapsed_seconds':elapsed, 'usage':usage,
              'usage_known':usage is not None, 'recovered_without_call':recovered,
              'model_reported':None, 'billing':'chatgpt_subscription', 'estimated_api_cost_usd':None}
    if not errors:
        record['coverage'] = coverage(answer, inp, meta['expected_result'])
    write(out / 'record.json', record)
    return record


def recover_active(active_file=ACTIVE):
    if not active_file.exists():
        return
    active = read(active_file)
    if active['state'] != 'in_flight':
        return
    run_dir = Path(active['run_dir']).resolve()
    if not run_dir.is_relative_to(LOCAL.resolve()):
        raise RuntimeError('Active-call journal points outside ignored local tree')
    meta = next(m for m in read(run_dir / 'index.json') if m['context_id'] == active['context_id'])
    out = run_dir / 'results' / meta['context_id']
    if not (out / 'record.json').exists():
        events, _, _ = events_and_usage(out / 'stdout.jsonl')
        if not any(e.get('type') == 'turn.completed' for e in events):
            raise RuntimeError('Interrupted call needs reconciliation; no new calls/retries permitted')
        finalize(run_dir, meta, recovered=True)
    write(active_file, {**active, 'state':'recorded', 'reconciled_at':now()}, replace=True)


def execute(run_dir, meta, pre, *, timeout=240, active_file=ACTIVE):
    out = run_dir / 'results' / meta['context_id']
    if (out / 'record.json').exists():
        return read(out / 'record.json')
    if (out / 'intent.json').exists():
        raise RuntimeError('Existing unrecorded intent cannot be retried')
    inp = read(run_dir / 'inputs' / (meta['context_id'] + '.json'))
    intent = {'context_id':meta['context_id'], 'case_id':meta['case_id'],
              'input_sha256':meta['input_sha256'], 'started_at':now(),
              'model_requested':MODEL, 'reasoning_effort':'medium',
              'cli_version':pre['cli_version'], 'authentication':pre['authentication']}
    write(out / 'intent.json', intent)
    write(active_file, {'state':'in_flight', 'run_dir':str(run_dir.resolve()),
                       'context_id':meta['context_id'], 'started_at':intent['started_at']}, replace=True)
    started, returncode, error = time.perf_counter(), None, None
    # Output goes directly to durable files before any parsing/validation.
    try:
        with tempfile.TemporaryDirectory(prefix='outwise-judge-v2-') as folder:
            temp = Path(folder)
            (temp / 'instructions.md').write_text((run_dir / 'prompt.md').read_text(encoding='utf-8'), encoding='utf-8')
            write(temp / 'schema.json', read(run_dir / 'schema.json'))
            command = legacy.codex_command(pre['cli'], temp, {'codex_model':MODEL}, output=False)
            write(out / 'command.json', {'argv':command, 'api_credentials_removed':True})
            with (out / 'stdout.jsonl').open('xb') as stdout, (out / 'stderr.txt').open('xb') as stderr:
                process = subprocess.Popen(command, cwd=temp, env=legacy.codex_environment(),
                                           stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
                try:
                    process.communicate(input=json.dumps(inp, ensure_ascii=False).encode('utf-8'), timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    error = 'CLI timeout; no automatic retry'
                returncode = process.returncode
                stdout.flush()
                stderr.flush()
                os.fsync(stdout.fileno())
                os.fsync(stderr.fileno())
    except Exception as exc:
        error = 'runtime:' + type(exc).__name__  # Never persist exception secret values.
    record = finalize(run_dir, meta, returncode=returncode,
                      elapsed=time.perf_counter()-started, error=error)
    write(active_file, {'state':'recorded', 'run_dir':str(run_dir.resolve()),
                       'context_id':meta['context_id'], 'finished_at':now()}, replace=True)
    return record
