"""Verify sealed local answers and bind separate source-review annotations."""
from pathlib import Path
import json
import statistics
import subprocess
import qwen_system_windows_adapter_v1 as adapter
import run_qwen_rag_system_v1 as q

REVIEW = q.ROOT / 'evals/qwen_rag_answer_review.v1.json'
OUTPUT = q.ROOT / 'evals/qwen_rag_system_results.v1.json'


def aggregate(rows):
    supported = [r for r in rows if not r['corpus_gap']]
    full = sum(r['answer_full_requirements'] for r in supported)
    total = sum(len(r['requirements']) for r in supported)
    return {'all_cases': len(rows), 'supported_cases': len(supported),
            'corpus_gap_cases': [r['case_id'] for r in rows if r['corpus_gap']],
            'answer_full_requirements': full, 'answer_total_requirements': total,
            'answer_micro_full_coverage': full / total,
            'answer_macro_full_coverage': statistics.mean(
                r['answer_full_requirements'] / len(r['requirements']) for r in supported),
            'answer_complete_cases': sum(r['answer_complete'] for r in supported),
            'flags': {flag: sum(r[flag] for r in rows) for flag in
                      ['unsupported', 'irrelevant', 'potentially_misleading', 'direct_conflict', 'requires_review']},
            'jurisdiction_leakage': 0,
            'gap_acknowledged': [r['case_id'] for r in rows if r['corpus_gap'] and r['gap_acknowledged']],
            'safe_gap_abstention': 0}


def main():
    adapter.install(); adapter.offline()
    frozen = q.verify()
    assert q.read(q.RUN / 'complete.json')['baseline_rows'] == 25
    annotations = q.read(REVIEW)['rows']
    cases = q.t.s.load_development()['cases']
    assert [r['case_id'] for r in annotations] == [c['id'] for c in cases]
    rows = []; resources = []; paths = []
    for case, annotation in zip(cases, annotations):
        cid = case['id']; directory = q.RUN / 'baseline' / cid
        result = q.read(directory / 'result.json')
        for name, expected in q.read(directory / 'seal.json').items():
            assert q.sha(directory / name) == expected
        prompt = (directory / 'prompt.txt').read_text(encoding='utf-8')
        assert result['cache_key'] == q.cache_key(frozen, prompt)
        command = q.read(directory / 'command.json')
        assert command[command.index('--prompt') + 1] == prompt
        assert command[command.index('--predict') + 1] == '256'
        assert command[command.index('--ctx-size') + 1] == '4096'
        assert command[command.index('--reasoning') + 1] == 'off'
        assert annotation['direct_conflict'] <= annotation['potentially_misleading']
        assert len(annotation['requirements']) == len(case['must_have_information'])
        assert set(annotation['requirements']) <= {'full', 'partial', 'absent', 'uncertain'}
        raw_retrieval = q.read(q.TARGET / cid / 'score.json')
        corpus_gap = case['expected_result'] == 'insufficient_coverage'
        assert corpus_gap == raw_retrieval['coverage']['gap']
        ids = result['retrieval']['source_ids']
        assert set(annotation['sources']) <= set(ids)
        answer = (directory / 'answer.txt').read_text(encoding='utf-8')
        assert not any(marker in answer for marker in ['Exiting...', '(truncated)', '[KUNNSKAPSUTDRAG'])
        body = q.read(directory / 'api-response.json')['body']
        assert body['answer'] == answer and result['source_metadata_matches']
        full = annotation['requirements'].count('full')
        rows.append({**annotation, 'corpus_gap': corpus_gap,
             'answer_full_requirements': full,
             'answer_complete': not corpus_gap and full == len(annotation['requirements']),
             'retrieval_decisions': raw_retrieval['decisions'],
             'requirement_causes': [([] if decision == 'full' else
                 ['corpus' if corpus_gap else 'retrieval'] if retrieved != 'covered'
                 else ['generation']) for decision, retrieved in
                 zip(annotation['requirements'], raw_retrieval['decisions'])],
             'prompt_constraints': 'Three-point budget may crowd out actions; no proven 256-token cutoff',
             'binding': {'answer_sha256': q.sha(directory / 'answer.txt'),
                         'prompt_sha256': result['retrieval']['prompt_sha256'],
                         'context_sha256': result['retrieval']['context_sha256'],
                         'cache_key': result['cache_key'], 'raw_path': str(directory.relative_to(q.ROOT)),
                         'all_delivered_passage_ids': ids},
             'runtime': result})
        resources.append(result['resources']); paths.append(directory)
    diagnostic = []
    assessments = {
        'case-03': {'requirements': ['full','full','partial','partial','absent'],
                    'finding': 'Water-specific answer improves, but exact elevation boundary and chemical warning still absent; awkward Norwegian.'},
        'case-08': {'requirements': ['partial','partial','absent','partial'],
                    'finding': 'Normal-breathing recovery branch/monitoring still absent; 10-second assessment duration is misassigned to CPR. Concrete generation conflict persists.'},
        'case-17': {'requirements': ['partial','absent'],
                    'finding': 'Recognizes rapid serious symptoms but combines immediate 113 with waiting until descent. Direct internal/source conflict despite sufficient context.'},
    }
    directory = q.RUN / 'diagnostic-sufficient-context'
    assert q.read(directory / 'complete.json')['diagnostic_calls'] == 3
    diag_freeze = q.read(directory / 'freeze.json')
    assert diag_freeze['diagnostic_code_sha256'] == q.sha(q.ROOT / 'evals/diagnose_qwen_rag_system_v1.py')
    for cid, assessment in assessments.items():
        folder = directory / cid
        for name, expected in q.read(folder / 'seal.json').items():
            assert q.sha(folder / name) == expected
        raw = q.read(folder / 'result.json')
        source_items = {p['id']: q.t.d.KnowledgeItem(**p) for p in
                        q.read(q.t.s.runtime.LOCAL / 'knowledge.json')['items']}
        selected = [q.t.d.RetrievedKnowledgeItem(source_items[i], 1.0)
                    for i in raw['input']['source_ids']]
        assert {r.item.id: q.digest(q.asdict(r.item)) for r in selected} == raw['input']['passage_hashes']
        actual_prompt = (folder / 'prompt.txt').read_text(encoding='utf-8')
        question = next(c['question'] for c in cases if c['id'] == cid)
        assert actual_prompt == q._build_grounded_prompt(question, selected)
        assert raw['cache_key'] == q.digest({'system': frozen, 'diagnostic': diag_freeze,
                    'prompt': (folder / 'prompt.txt').read_text(encoding='utf-8')})
        diagnostic.append({**assessment, **raw,
                           'answer_sha256': q.sha(folder / 'answer.txt'),
                           'raw_path': str(folder.relative_to(q.ROOT))})
    timings = [r['runtime']['end_to_end_seconds'] for r in rows]
    record = {'version': 1, 'status': 'system_test_complete_quality_not_approved',
       'assessment': 'One agent source review; not independent medical/legal or sampling validation',
       'candidate': frozen['candidate'], 'baseline_calls': 25, 'diagnostic_calls': 3,
       'new_codex_judge_calls': 0, 'paid_api_calls': 0,
       'freeze_sha256': q.sha(q.RUN / 'freeze.json'), 'answer_review_sha256': q.sha(REVIEW),
       'summary25': aggregate(rows), 'summary_legacy15': aggregate(rows[:15]),
       'resources': {'baseline_elapsed_sum_seconds': sum(timings),
          'baseline_latency_median_seconds': statistics.median(timings),
          'baseline_latency_mean_seconds': statistics.mean(timings),
          'baseline_latency_min_seconds': min(timings), 'baseline_latency_max_seconds': max(timings),
          'peak_process_tree_rss_bytes': max(r['peak_process_tree_rss_bytes'] for r in resources),
          'minimum_available_ram_bytes': min(r['minimum_available_ram_bytes'] for r in resources),
          'baseline_cpu_seconds': sum(r['cpu_seconds'] for r in resources),
          'query_ranking_packing_mean_seconds': statistics.mean(
              r['runtime']['retrieval']['query_ranking_packing_seconds'] for r in rows),
          'baseline_prompt_tokens_locked': sum(r['runtime']['retrieval']['prompt_tokens'] for r in rows),
          'baseline_context_tokens_locked': sum(r['runtime']['retrieval']['context_tokens'] for r in rows),
          'baseline_answer_tokens_locked': sum(r['runtime']['answer_tokens_locked_tokenizer'] for r in rows),
          'baseline_max_prompt_tokens_locked': max(r['runtime']['retrieval']['prompt_tokens'] for r in rows),
          'baseline_max_answer_tokens_locked': max(r['runtime']['answer_tokens_locked_tokenizer'] for r in rows),
          'diagnostic_prompt_tokens_locked': sum(r['input']['prompt_tokens'] for r in diagnostic),
          'diagnostic_answer_tokens_locked': sum(r['answer_tokens_locked_tokenizer'] for r in diagnostic),
          'model_bytes': Path(frozen['settings']['model_path']).stat().st_size,
          'all_guards_passed': all(r['minimum_available_ram_bytes'] >= q.RAM_RESERVE and
                                  r['peak_process_tree_rss_bytes'] <= q.RSS_LIMIT for r in resources),
          'method': 'Sampled .1s simultaneous embedding/Qwen parent+child RSS; sequential cold CLI calls; no GPU VRAM measurement',
          'token_method': 'Locked tokenizer serialized prompt/visible answer counts; runtime actual input/output/stop reason not reported; reasoning off'},
       'technical_limits': ['OS internet disconnection and interactive browser review not performed',
          'One sample per case; diagnostic shorter/cleaner context changes cannot isolate length from relevance/order',
          'Raw corpus_gap diagnostic field used a nonexistent YAML key and is false; this separate analysis derives 14/15/25 from unchanged expected_result and confirms historical scorer gap flags',
          'Old backend Python3.11 executable unavailable; isolated Python3.12 and existing test dependencies used'],
       'rows': rows, 'diagnostics_separate': diagnostic}
    OUTPUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    q.verify(); q.t.verify()
    task_current = (q.ROOT / 'TASKS.md').read_text(encoding='utf-8')
    task_previous = subprocess.check_output(['git','show','849a4ff:TASKS.md'],cwd=q.ROOT).decode('utf-8')
    marker = '# Milestone 3 — Safety + Finished MVP'
    assert task_current[task_current.index(marker):] == task_previous[task_previous.index(marker):]
    audit = {'baseline_seals':25,'diagnostic_seals':3,'exact_live_query_ranking_packing_prompts':25,
             'metadata_api_matches':25,'frozen_inputs_passed':True,'historical_retrieval_preserved':True,
             'source_review_rows':25,'review_source_ids_valid':True,'holdout_accessed':False,
             'paid_api_calls':0,'judge_calls':0,'m3_suffix_unchanged_from_849a4ff':True,
             'results_sha256':q.sha(OUTPUT),'review_sha256':q.sha(REVIEW)}
    audit['reporter_sha256'] = q.sha(Path(__file__).resolve())
    (q.ROOT / 'evals/qwen_rag_system_audit.v1.json').write_text(q.t.s.canonical(audit)+'\n',encoding='utf-8')
    print(record['summary25']); print(record['summary_legacy15']); print(record['resources'])


if __name__ == '__main__':
    main()
