"""Frozen metadata compatibility for targeted rows; does not alter judge input."""
from pathlib import Path
import argparse

import run_targeted_retrieval_v1 as t

s = t.s
ORIGINAL = s.score_saved
STATE = t.RUN / 'scoring-metadata-v1'


def complete_metadata(row):
    count = len({(e['item'].get('document_id'), e['item'].get('section'))
                 for e in row['excerpts']})
    if 'section_count' in row and row['section_count'] != count:
        raise ValueError('Recorded section count differs from delivered excerpts')
    assert row['chunk_count'] == len(row['excerpts'])
    return {**row, 'section_count': count}


def score_saved(case, row, context, corpus, rules):
    return ORIGINAL(case, complete_metadata(row), context, corpus, rules)


def install():
    # Only the proof's returned diagnostic metadata was incomplete. All source
    # matching, proof decisions, judge merging and judge/cache inputs stay intact.
    assert s.score_saved in (ORIGINAL, score_saved)
    s.score_saved = score_saved


def binding():
    files = {}
    cases = {c['id']: c for c in s.load_development()['cases']}
    corpus = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
    for cid in ['T-ranking', 'T-packing', 'T-combined']:
        target = t.RUN / 'configurations' / cid
        files[str((target / 'retrieved-all.json').relative_to(t.RUN))] = t.d.file_hash(target / 'retrieved-all.json')
        for row in s.runtime.read(target / 'retrieved-all.json'):
            complete_metadata(row)
            case = cases[row['case_id']]
            assert s.judge_input(case, row) == s.judge_input(case, complete_metadata(row))
            payload = s.judge_input(case, row)
            proof = score_saved(case, row, '\n\n'.join(b['text'] for b in payload['blocks']), corpus, s.rules())
            assert not proof['provenance_issues']
            for name in ['retrieved.json', 'context.txt', 'prompt-not-executed.txt']:
                path = target / row['case_id'] / name
                files[str(path.relative_to(t.RUN))] = t.d.file_hash(path)
    return {'reason': 'Missing diagnostic section_count in targeted rows; no scoring-rule or judge-input change',
            'original_freeze_sha256': t.d.file_hash(t.RUN / 'freeze.json'),
            'code': {str(p.relative_to(s.ROOT)): t.d.file_hash(p) for p in
                     [Path(__file__), s.ROOT / 'evals/test_targeted_metadata_v1.py']},
            'retrieval_files': files, 'judge_inputs_unchanged': 75,
            'original_rows_modified': 0, 'judge_identity': s.runtime.read(t.RUN / 'freeze.json')['judge_identity']}


def verify_binding():
    value = binding()
    t.write_once(STATE / 'freeze.json', value)
    return value


if __name__ == '__main__':
    s.holdout_guard()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'score'])
    parser.add_argument('--config-id', choices=['T-ranking', 'T-packing', 'T-combined'])
    args = parser.parse_args()
    with s.runtime.JudgeLock(t.d.EXPERIMENT_LOCK):
        try:
            t.verify(); verify_binding(); install()
            if args.command == 'score':
                assert args.config_id
                t.score(args.config_id); t.export('running')
            else:
                print('75 unchanged judge inputs; section-count metadata adapter frozen', flush=True)
        except Exception as error:
            t.export('blocked', str(error)); raise
