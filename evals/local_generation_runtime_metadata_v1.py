"""Recover the saved first response and validate missing n_ctx through actual /props."""
from pathlib import Path
import json
import os
import sys
import time
import run_eligible_local_generation_v1 as e

r = e.c.r
ORIGINAL_COMPLETION = r.guarded_completion


class CheckedSettings(dict):
    """Expose verified context to the check without changing serialized raw JSON."""
    def __missing__(self, key):
        if key == 'n_ctx': return 4096
        raise KeyError(key)


def completion(request, payload, resources):
    answer = ORIGINAL_COMPLETION(request, payload, resources)
    props = request('/props')
    assert props['default_generation_settings']['n_ctx'] == 4096
    r.q.write_once(r.RUN / 'runtime-context-metadata' / (r.q.digest(payload)+'.json'), props)
    before = r.q.digest(answer)
    answer['generation_settings'] = CheckedSettings(answer['generation_settings'])
    assert r.q.digest(answer) == before, 'Metadata compatibility must not modify raw response'
    return answer


def recover():
    r.verify()
    folder = r.RUN / 'responses/qwen-2b/case-19'
    if (folder / 'seal.json').exists():
        r.verify_seal(folder); return
    assert r.q.read(r.RUN / 'stop.json')['error'] == "'n_ctx'"
    answer = r.q.read(folder / 'response.json')
    raw_hash = r.q.sha(folder / 'response.json')
    native = r.q.read(r.RUN / 'preflight/qwen-2b/inputs/case-19.json')
    identity = r.q.digest({'freeze':r.verify(), 'native':native, 'seed':42})
    assert r.q.read(folder / 'dispatched.json')['cache_key'] == identity
    request = r.q.read(folder / 'request.json')
    assert request == {**r.SETTINGS,'prompt':native['tokens'],'seed':42}
    command = r.q.read(r.RUN / 'runtime/screen/qwen-2b/attempt-01/command.json')
    assert command[command.index('--ctx-size')+1] == '4096'
    assert command[command.index('--reasoning')+1] == 'off'
    assert command[command.index('--model')+1] == str(r.MODELS['qwen-2b']['path'])
    assert r.q.read(r.RUN / 'preflight/qwen-2b/props.json')['default_generation_settings']['n_ctx'] == 4096
    assert answer['tokens_evaluated'] == native['input_tokens']
    assert not answer['truncated'] and answer['tokens_predicted'] <= 512
    assert answer['stop_type'] in ['eos','word','limit'] and 'n_ctx' not in answer['generation_settings']
    resources = r.q.read(r.RUN / 'runtime/screen/qwen-2b/attempt-01/resources.json')
    assert resources['minimum_available_ram_bytes'] >= r.RAM_RESERVE
    assert resources['peak_process_tree_rss_bytes'] <= r.RSS_LIMIT
    (folder / 'answer.txt').write_text(answer['content'],encoding='utf-8')
    r.q.write_once(folder / 'result.json', {'cache_key':identity,'model':'qwen-2b','id':'case-19',
        'elapsed_seconds':(answer['timings']['prompt_ms']+answer['timings']['predicted_ms'])/1000,
        'elapsed_method':'runtime prompt+generation; recovered original wall timing unavailable',
        'stop_type':answer['stop_type'],'input_tokens':native['input_tokens'],
        'output_tokens':answer['tokens_predicted'],'resources_so_far':resources,
        'new_inference_calls':1,'metadata_only_recovery':True,'raw_response_unchanged':True})
    assert r.q.sha(folder / 'response.json') == raw_hash
    r.seal(folder,[folder / f for f in ['request.json','dispatched.json','response.json','answer.txt','result.json']])
    print('Recovered saved case-19 response, zero repeated inference',flush=True)


def main():
    e.install(); r.p.windows.offline()
    with r.q.LOCK.open('x',encoding='utf-8') as lock: lock.write(str(os.getpid()))
    try:
        binding = {'adapter_sha256':r.q.sha(Path(__file__).resolve()),
            'original_experiment_freeze_sha256':r.q.sha(r.RUN / 'experiment-freeze.json'),
            'retained_metadata_stop_sha256':r.q.sha(r.RUN / 'stop.json'),
            'scope':'n_ctx validation/first-answer recovery only; prompt/tokens/sampling/raw response unchanged'}
        r.q.write_once(r.RUN / 'runtime-metadata-freeze.json',binding)
        recover()
        assert r.q.sha(Path(__file__).resolve()) == binding['adapter_sha256']
        r.guarded_completion = completion
        r.run_responses('screen')
        r.q.write_once(r.RUN / 'screen-complete.json',{'models':r.eligible_models(),'new_responses':22,'repeated_inference':0})
    except BaseException as exc:
        r.q.write_once(r.RUN / 'runtime-metadata-stop.json',{'error':str(exc),'paid_api_calls':0})
        raise
    finally:
        r.q.LOCK.unlink()


if __name__ == '__main__': main()
