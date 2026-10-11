"""Offline verification of the retained pre-inference stop; never calls a model."""
from pathlib import Path
import subprocess
import preflight_local_generation_v1 as p


def main():
    p.windows.offline()
    q = p.q
    frozen = q.read(p.RUN / 'input-freeze.json')
    for name, expected in {**frozen['historical_freeze']['identities'],
                           **frozen['identities']}.items():
        assert q.sha(Path(name)) == expected, name
    cases = q.t.s.load_development()['cases']
    assert [r['id'] for r in frozen['inputs'][:25]] == [c['id'] for c in cases]
    assert len(frozen['inputs']) == 36
    for item in frozen['inputs']:
        context = Path(item['context_path']).read_text(encoding='utf-8')
        assert p.hashlib.sha256(context.encode()).hexdigest() == item['context_sha256']
        assert item['messages'] == p.messages(item['question'], context)
    for case in cases:
        folder = p.OLD / 'baseline' / case['id']
        for name, expected in q.read(folder / 'seal.json').items():
            assert q.sha(folder / name) == expected
    for cid in ['case-03','case-08','case-17']:
        folder = p.OLD / 'diagnostic-sufficient-context' / cid
        for name, expected in q.read(folder / 'seal.json').items():
            assert q.sha(folder / name) == expected
    old_rows = q.read(p.ROOT / 'evals/qwen_rag_system_results.v1.json')['rows']
    covered = sum(r['retrieval_decisions'].count('covered') for r in old_rows if not r['corpus_gap'])
    preserved = sum(a == 'full' and d == 'covered' for r in old_rows if not r['corpus_gap']
                    for a,d in zip(r['requirements'], r['retrieval_decisions']))
    assert (covered, preserved) == (60,15)
    current_tasks = (p.ROOT / 'TASKS.md').read_text(encoding='utf-8')
    old_tasks = subprocess.run(['git','show','3d11315:TASKS.md'], check=True,
                              capture_output=True, encoding='utf-8').stdout
    marker = '# Milestone 3 — Safety + Finished MVP'
    assert current_tasks[current_tasks.index(marker):] == old_tasks[old_tasks.index(marker):]
    stop = q.read(p.RUN / 'stop.json')
    resources = q.read(p.RUN / 'preflight/qwen-2b/resources.json')
    assert stop['inference_calls'] == stop['paid_api_calls'] == 0
    assert resources['minimum_available_ram_bytes'] < frozen['limits']['ram_reserve_bytes']
    assert resources['peak_process_tree_rss_bytes'] < frozen['limits']['rss_limit_bytes']
    assert not (p.RUN / 'preflight/qwen-2b/props.json').exists()
    assert not (p.RUN / 'preflight/qwen-2b/complete.json').exists()
    log = (p.RUN / 'preflight/qwen-2b/stderr.txt').read_text(encoding='utf-8')
    assert 'loading model' in log and 'processing prompt' not in log
    artifacts = [p.RUN / 'input-freeze.json', p.RUN / 'stop.json']
    artifacts += [p.RUN / 'preflight/qwen-2b' / name for name in
                  ['command.json','stdout.txt','stderr.txt','resources.json']]
    artifacts += [p.RUN.parent / 'stop.json']
    record = {'version': 1, 'status': 'integrity_passed_resource_preflight_failed',
              'planned_input_definitions': 36, 'old_baseline_seals_verified': 25,
              'old_diagnostic_seals_verified': 3, 'historical_identities_verified': True,
              'new_input_identities_verified': True, 'm3_tasks_unchanged': True,
              'new_inference_calls': 0, 'new_codex_judge_calls': 0, 'paid_api_calls': 0,
              'downloaded_model_variants': 0, 'runtime_token_budget_verified': False,
              'system_role_verified': False, 'all_models_compatibility_verified': False,
              'host_ram_guard_passed': False, 'process_rss_guard_passed': True,
              'resources': resources, 'old_covered_requirements': covered,
              'old_full_answers_with_retrieved_support': preserved,
              'old_covered_requirements_partial_or_absent': covered-preserved,
              'raw_hashes': {str(path.relative_to(p.ROOT)):q.sha(path) for path in artifacts},
              'audit_code_sha256': q.sha(Path(__file__).resolve()),
              'tests': 'Three input-budget/source-preservation/plan unit checks passed; actual runtime stopped before ready'}
    q.write_once(p.ROOT / 'evals/local_generation_comparison_preflight.v1.json', record)
    print('Retained preflight verified: 36 frozen inputs, 28 historical seals, RAM stop, zero inference; M3 unchanged')


if __name__ == '__main__':
    main()
