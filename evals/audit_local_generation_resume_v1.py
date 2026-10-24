"""Verify the successful control preflight and retained 4B RAM stop offline."""
from pathlib import Path
import subprocess
import resume_local_generation_v1 as r


def main():
    r.p.windows.offline()
    frozen = r.plan()
    root = r.RUN
    control = root / 'preflight/qwen-2b'
    larger = root / 'preflight/qwen-4b'
    r.verify_seal(control)
    complete = r.q.read(control / 'complete.json')
    inputs = [r.q.read(control / 'inputs' / (item['id'] + '.json')) for item in frozen['inputs']]
    assert len(inputs) == complete['inputs'] == 36
    for item, row in zip(frozen['inputs'],inputs):
        assert row['id'] == item['id'] and row['context_sha256'] == item['context_sha256']
        assert all(turn['content'] in row['prompt'] for turn in item['messages'])
        assert len(row['tokens']) == row['input_tokens']
        r.p.budget_check(row['input_tokens'],row['actual_context'],row['training_context'])
    model = r.MODELS['qwen-4b']['path']
    manifest = r.q.read(root / 'downloads/qwen-4b/manifest.json')
    assert r.q.sha(model) == manifest['sha256'] and model.stat().st_size == manifest['size']
    assert r.q.sha(r.MODELS['qwen-2b']['path']) == complete['model_sha256']
    resources = {name:r.q.read(root / 'preflight' / name / 'resources.json') for name in ['qwen-2b','qwen-4b']}
    assert resources['qwen-2b']['minimum_available_ram_bytes'] >= r.RAM_RESERVE
    assert resources['qwen-2b']['peak_process_tree_rss_bytes'] <= r.RSS_LIMIT
    assert resources['qwen-4b']['minimum_available_ram_bytes'] < r.RAM_RESERVE
    assert resources['qwen-4b']['peak_process_tree_rss_bytes'] < r.RSS_LIMIT
    assert not (root / 'responses').exists() and not (root / 'experiment-freeze.json').exists()
    assert not (larger / 'props.json').exists()
    previous = subprocess.run(['git','show','3e9bafd:TASKS.md'],check=True,capture_output=True,encoding='utf-8').stdout
    tasks = (r.p.ROOT / 'TASKS.md').read_text(encoding='utf-8')
    marker = '# Milestone 3 — Safety + Finished MVP'
    assert tasks[tasks.index(marker):] == previous[previous.index(marker):]
    paths = [root / 'stop.json', root.parent / 'stop.json',
             root / 'downloads/qwen-4b/manifest.json', control / 'seal.json']
    paths += [directory / name for directory in [control,larger] for name in
              ['command.json','stdout.txt','stderr.txt','resources.json']]
    output = {'version':2,'status':'control_preflight_passed_larger_model_host_ram_stop',
        'date':'2026-10-24','original_input_freeze_sha256':r.q.sha(r.p.RUN / 'input-freeze.json'),
        'historical_and_input_identities_verified':True,'planned_input_count':36,
        'control_passed_inputs':36,'control_min_input_tokens':min(i['input_tokens'] for i in inputs),
        'control_max_input_tokens':max(i['input_tokens'] for i in inputs),
        'runtime_context':4096,'reserved_output_tokens':512,'input_budget':3200,
        'control_training_context':262144,'resources':resources,'model_4b':manifest,
        'new_generated_responses':0,'new_codex_judge_calls':0,'paid_api_calls':0,
        'model_4b_runtime_passed':False,'gemma_downloaded':False,'m3_tasks_unchanged':True,
        'all_model_experiment_frozen':False,'inference_orchestration_runtime_tested':False,
        'raw_hashes':{str(path.relative_to(r.p.ROOT)):r.q.sha(path) for path in paths},
        'code_sha256':{path.name:r.q.sha(path) for path in [Path(__file__).resolve(),Path(r.__file__).resolve()]}}
    destination = r.p.ROOT / 'evals/local_generation_comparison_preflight.v2.json'
    r.q.write_once(destination,output)
    # Public JSON uses LF; local historical logs and seal bytes are untouched.
    destination.write_text(destination.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    print('Audit passed: exact 36-input control, verified 4B download, retained host RAM stop, zero responses; M3 unchanged')


if __name__ == '__main__': main()
