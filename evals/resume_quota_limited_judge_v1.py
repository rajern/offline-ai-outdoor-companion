"""Explicit owner resume of one recorded quota rejection; no inference or retries.

Successful, ambiguous, incomplete and sealed results cannot be moved. The failed
record and every log remain in a hashed, versioned archive and separate ledger.
"""
import argparse
import json
from pathlib import Path

import continue_retrieval_optimization_v1 as c
import run_retrieval_optimization_v1 as d
import retrieval_optimization_scoring as s
from optimization_resources import Resources


def archive_quota_rejection(key, authorization):
    s.holdout_guard()
    if len(key) != 64 or any(v not in '0123456789abcdef' for v in key):
        raise ValueError('Invalid cache key')
    if not authorization.strip():
        raise ValueError('Explicit owner resume instruction required')
    with s.runtime.JudgeLock(d.EXPERIMENT_LOCK), s.runtime.JudgeLock():
        c.check_frozen()
        s.runtime.recover_active()
        pre = s.runtime.preflight()
        assert s.identity(pre) == s.runtime.read(d.RUN / 'freeze.json')['judge_identity']
        with Resources() as resources:
            resources.check()
        cache = (s.CACHE / key).resolve()
        assert cache.is_relative_to(s.CACHE.resolve())
        out = cache / 'results/context-01'
        assert out.resolve().is_relative_to(cache)
        record = s.runtime.read(out / 'record.json')
        events, malformed, usage = s.runtime.events_and_usage(out / 'stdout.jsonl')
        assert record['success'] is False and record['returncode'] != 0
        assert not malformed and usage is None and record['usage'] is None
        assert not (out / 'answer.json').exists() and not (cache / 'result-seal.json').exists()
        assert not any(e.get('type') == 'turn.completed' for e in events)
        assert any(e.get('type') == 'turn.failed' and 'usage limit' in e.get('error', {}).get('message', '').lower() for e in events)
        requests = [json.loads(line) for line in (d.RUN / 'judge-requests.jsonl').read_text(encoding='utf-8').splitlines()]
        request = next(r for r in reversed(requests) if r['cache_key'] == key)
        assert not (d.RUN / 'configurations' / request['configuration'] / request['case_id'] / 'score.json').exists()
        payload = s.runtime.read(cache / 'inputs/context-01.json')
        assert s.cache_key(payload, s.runtime.read(cache / 'identity.json')) == key
        assert payload['case_id'] == record['case_id'] == request['case_id']
        archives = cache / 'failed-attempts/context-01'
        archives.mkdir(parents=True, exist_ok=True)
        destination = (archives / f'attempt-{len(list(archives.glob("attempt-*"))) + 1:03}').resolve()
        assert destination.is_relative_to(cache) and not destination.exists()
        hashes = {p.name: d.file_hash(p) for p in out.iterdir() if p.is_file()}
        # Intent is saved first so a crash cannot erase the accounting evidence.
        manifest = {'at': s.runtime.now(), 'authorization': authorization, **request,
                    'archive': str(destination.relative_to(s.ROOT)), 'file_sha256': hashes,
                    'failed_record': record, 'resource_check': resources.result(),
                    'reason': 'Recorded quota rejection; natural quota reset and explicit owner resume.',
                    'completed_answers_repeated': 0, 'inference_calls_in_preparation': 0}
        ledger = c.STATE / 'quota-retry-archives'
        ledger.mkdir(parents=True, exist_ok=True)
        manifest_path = ledger / (key + '-' + destination.name + '.json')
        s.runtime.write(manifest_path, manifest)
        out.rename(destination)
        assert all(d.file_hash(destination / name) == value for name, value in hashes.items())
        print(json.dumps({'archived': key, 'configuration': request['configuration'], 'case_id': record['case_id'],
                          'retained_failure_seconds': record['elapsed_seconds'], 'new_judge_calls': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-key', required=True)
    parser.add_argument('--owner-resume', required=True)
    args = parser.parse_args()
    archive_quota_rejection(args.cache_key, args.owner_resume)
