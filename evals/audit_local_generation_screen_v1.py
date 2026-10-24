"""Final offline integrity/usage audit of bounded generation screening."""
from pathlib import Path
import math
import subprocess
import run_eligible_local_generation_v1 as e

r=e.c.r


def main():
    r.p.windows.offline();r.RUN=e.RUN
    frozen=r.verify()
    supplement=r.q.read(r.RUN/'runtime-metadata-freeze.json')
    assert supplement['adapter_sha256']==r.q.sha(r.p.ROOT/'evals/local_generation_runtime_metadata_v1.py')
    assert supplement['original_experiment_freeze_sha256']==r.q.sha(r.RUN/'experiment-freeze.json')
    result_path=r.p.ROOT/'evals/local_generation_comparison_results.v1.json'
    results=r.q.read(result_path)
    assert results['assessment_code_sha256']==r.q.sha(r.p.ROOT/'evals/review_local_generation_screen_v1.py')
    assert results['new_responses']==len(results['rows'])==22
    assert results['old_2b_same_screen8']['flags']['critical_error'] is None
    dispatch=list((r.RUN/'responses').glob('*/*/dispatched.json'))
    responses=list((r.RUN/'responses').glob('*/*/response.json'))
    assert len(dispatch)==len(responses)==22
    inputs={item['id']:item for item in r.plan()['inputs']}
    snapshots={}
    for row in results['rows']:
        model=row['model'];key=row['id'];folder=r.RUN/'responses'/model/key
        r.verify_seal(folder)
        response=r.q.read(folder/'response.json');request=r.q.read(folder/'request.json')
        native=r.q.read(r.RUN/'preflight'/model/'inputs'/(key+'.json'))
        assert request=={**r.SETTINGS,'seed':inputs[key]['seed'],'prompt':native['tokens']}
        assert response['tokens_evaluated']==len(native['tokens'])==native['input_tokens']<=3200
        assert response['tokens_predicted']<=512 and not response['truncated']
        assert response['stop_type'] in ['eos','limit','word']
        setting=response['generation_settings']
        assert setting['seed']==42 and setting['top_k']==20 and setting['n_predict']==512
        assert math.isclose(setting['temperature'],.2,abs_tol=1e-6)
        assert math.isclose(setting['top_p'],.8,abs_tol=1e-6)
        assert row['binding']['answer_sha256']==r.q.sha(folder/'answer.txt')
        assert row['binding']['response_sha256']==r.q.sha(folder/'response.json')
        assert (folder/'answer.txt').read_text(encoding='utf-8')==response['content']
        assert '<think>' not in response['content']
        assert row['binding']['context_sha256']==inputs[key]['context_sha256']
        if not row['runtime'].get('metadata_only_recovery'):
            props=r.q.read(r.RUN/'runtime-context-metadata'/(r.q.digest(request)+'.json'))
            assert props['default_generation_settings']['n_ctx']==4096
            assert Path(props['model_path']).resolve()==r.MODELS[model]['path'].resolve()
        snapshots[str(folder.relative_to(r.p.ROOT))]=r.q.sha(folder/'seal.json')
    decision=r.q.read(r.RUN/'finalist-decision.json')
    assert not decision['eligible'] and decision['assessment_sha256']==r.q.sha(result_path)
    assert not (r.RUN/'runtime/finalist').exists()
    old_tasks=subprocess.run(['git','show','3e9bafd:TASKS.md'],check=True,capture_output=True,encoding='utf-8').stdout
    tasks=(r.p.ROOT/'TASKS.md').read_text(encoding='utf-8');marker='# Milestone 3 — Safety + Finished MVP'
    assert tasks[tasks.index(marker):]==old_tasks[old_tasks.index(marker):]
    raw=[r.RUN/name for name in ['experiment-freeze.json','runtime-metadata-freeze.json','screen-complete.json',
         'exclusions.json','stop.json','finalist-decision.json']]
    raw += [r.RUN/'downloads/gemma-e2b/manifest.json',r.RUN/'downloads/qwen-4b/manifest.json']
    audit={'version':1,'status':'bounded_screening_complete_no_eligible_finalist',
        'verified_responses':22,'verified_native_preflight_inputs':72,
        'actual_new_model_calls':22,'unnecessary_repeated_inference':0,
        'recovered_first_response_without_repeat':True,'paid_api_calls':0,'codex_judge_calls':0,
        'input_tokens':sum(m['input_tokens'] for m in results['resources'].values()),
        'output_tokens':sum(m['output_tokens'] for m in results['resources'].values()),
        'all_executed_generation_resource_guards_passed':all(m['all_generation_resource_guards_passed'] for m in results['resources'].values()),
        'four_b_resource_excluded':True,'first_runtime_metadata_stop_retained':True,
        'original_frozen_inputs_and_histories_verified':True,'m3_tasks_unchanged':True,
        'no_finalist_calls':True,'no_new_full25_result':True,'holdout_accessed':False,
        'results_sha256':r.q.sha(result_path),'response_seals':snapshots,
        'raw_hashes':{str(path.relative_to(r.p.ROOT)):r.q.sha(path) for path in raw},
        'audit_code_sha256':r.q.sha(Path(__file__).resolve()),
        'validation_limit':'Integrity/usage checks verify data, not independent clinical or legal correctness.'}
    target=r.p.ROOT/'evals/local_generation_comparison_final_audit.v1.json'
    r.q.write_once(target,audit)
    target.write_text(target.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    print('PASS: 22 sealed responses, 72 native inputs, resource guards, exact settings, cache/source identities; no finalist/API/M3')


if __name__=='__main__':main()
