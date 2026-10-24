"""Explicit owner retry; inherit successful preflight, never overwrite failed loads."""
from pathlib import Path
import shutil
import resume_local_generation_v1 as r

PREVIOUS = r.RUN
RETRY = r.p.ROOT / 'knowledge/local/diagnostics/local-generation-comparison-retry-2026-10-24'


def inherit():
    r.plan()
    old_control = PREVIOUS / 'preflight/qwen-2b'
    r.verify_seal(old_control)
    audit = r.q.read(r.p.ROOT / 'evals/local_generation_comparison_preflight.v2.json')
    paths = [old_control / name for name in r.q.read(old_control / 'seal.json')]
    paths += [old_control / 'seal.json', old_control / 'command.json',
              PREVIOUS / 'downloads/qwen-4b/manifest.json']
    for path in paths:
        public_hash = audit['raw_hashes'].get(str(path.relative_to(r.p.ROOT)))
        if public_hash: assert r.q.sha(path) == public_hash
        destination = RETRY / path.relative_to(PREVIOUS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            assert r.q.sha(destination) == r.q.sha(path)
        else:
            shutil.copyfile(path, destination)
    r.verify_seal(RETRY / 'preflight/qwen-2b')
    r.q.write_once(RETRY / 'resume-lineage.json', {
        'previous_stop_sha256': r.q.sha(PREVIOUS / 'stop.json'),
        'previous_input_freeze_sha256': r.q.sha(r.p.RUN / 'input-freeze.json'),
        'reused_control_seal_sha256': r.q.sha(old_control / 'seal.json'),
        'owner_instruction': 'prøv igjen', 'previous_attempt_preserved': True})


if __name__ == '__main__':
    r.q.t.s.holdout_guard()
    inherit()
    r.RUN = RETRY
    r.main()
