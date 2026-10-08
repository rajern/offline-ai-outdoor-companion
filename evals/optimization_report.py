"""Source-free public progress/report export from durable experiment records."""
from collections import Counter
import json
from pathlib import Path
import retrieval_optimization_scoring as s


def planned():
    return ([{'id':'A-'+m,'phase':'A','model':m,'k':8,'threshold':None,'packing':'P2'} for m in ['minilm','gemma2','qwen3-q4']]
        +[{'id':f'B-k{k}-{t}','phase':'B','model':None,'k':k,'threshold_name':t,'packing':'P2'}
          for k in [3,5,8,12,16] for t in ['none','p10','p30','p50','p70']]
        +[{'id':'C-'+p,'phase':'C','model':None,'k':None,'threshold':None,'packing':p} for p in ['P1','P2','P3']])


def consumption(run):
    start=run/'started.json'
    baseline=set(s.runtime.read(start)['existing_cache_keys']) if start.exists() else set()
    requests=[];log=run/'judge-requests.jsonl'
    if log.exists():requests=[json.loads(line) for line in log.read_text(encoding='utf-8').splitlines() if line.strip()]
    new_keys={r['cache_key'] for r in requests}-baseline
    totals=Counter();errors=[];calls=0;completed=0;elapsed=0;unknown=0
    for key in sorted(new_keys):
        directory=s.CACHE/key/'results/context-01'
        if not (directory/'intent.json').exists():continue
        calls+=1
        if not (directory/'record.json').exists():unknown+=1;errors.append({'cache_key':key,'status':'incomplete'});continue
        record=s.runtime.read(directory/'record.json');completed+=bool(record['success'])
        elapsed+=record.get('elapsed_seconds') or 0
        if record.get('usage'):
            for name,value in record['usage'].items():totals[name]+=value
        else:unknown+=1
        if not record['success']:errors.append({'cache_key':key,'status':'failed','validation_errors':record['validation_errors']})
    cached=0
    for path in (run/'configurations').glob('*/case-*/score.json'):
        cached+=bool(s.runtime.read(path)['cache_hit'])
    return {'actual_calls':calls,'successful_calls':completed,'cache_hits':cached,'avoided_calls':cached,
        'usage':dict(totals),'sum_call_seconds':elapsed,'unknown_usage_calls':unknown,'errors':errors,
        'billing':'ChatGPT subscription','paid_api_calls':0,'estimated_api_cost_usd':None}


def export(base,run,*,status,error=None):
    records=[]
    for config in planned():
        directory=run/'configurations'/config['id'];saved=directory/'config.json'
        if saved.exists():config={**config,**s.runtime.read(saved)}
        scores=[s.runtime.read(p) for p in sorted(directory.glob('case-*/score.json'))]
        retrieved=directory/'retrieved-all.json';summary=directory/'summary.json'
        row={'configuration':config,'status':'not_run','retrieved_cases':0,'judged_cases':len(scores),
            'full25':None,'legacy15':None,'resources':None,'review_cases':[r['case_id'] for r in scores if r['requires_review']],
            'partial_decisions':[{'case_id':r['case_id'],'decisions':r['decisions'],'flags':r['flags'],
                 'certificate_judge_disagreement':r['certificate_judge_disagreement'],'requires_review':r['requires_review']} for r in scores]}
        if retrieved.exists():row.update(status='retrieved',retrieved_cases=len(s.runtime.read(retrieved)))
        if scores:row['status']='partially_scored'
        if row['review_cases']:row['status']='blocked_review'
        if summary.exists():
            value=s.runtime.read(summary);row.update(status='complete',full25=value['full25'],legacy15=value['legacy15'],resources=value['resources'])
        records.append(row)
    technical=base/'technical-preflight/summary.json'
    preflight=s.runtime.read(technical) if technical.exists() else None
    indices={p.parent.name:s.runtime.read(p) for p in (run/'indices').glob('*/index.json')}
    choices={phase:s.runtime.read(run/f'choice-{phase}.json') for phase in ['A','B','C'] if (run/f'choice-{phase}.json').exists()}
    data={'date':'2026-10-08','status':status,'error':error,'planned_configurations':31,
        'completed_configurations':sum(r['status']=='complete' for r in records),
        'development_cases':25,'legacy_cases':15,'technical_preflight':preflight,
        'configurations':records,'indices':indices,'provisional_stage_choices':choices,
        'thresholds':s.runtime.read(run/'thresholds.json') if (run/'thresholds.json').exists() else None,
        'consumption':consumption(run),'holdout_accessed':False,'production_changed':False,'generation_calls':0,
        'recommendation':choices.get('C',{}).get('configuration') if status=='complete' else None,
        'historical_legacy15_reference':{'B8_original_manual_coverage':'34/51','complete_supported_cases':'7/13',
             'scope':'original 15 only; historical manual judgments differ from current V3 and adjudication; not a controlled delta'},
        'limitations':['Development/calibration, not independent product/safety validation.',
             'No mobile hardware benchmark; CPU/RAM and tokenizer measure this Windows machine.',
             'Exact judge server revision not exposed by CLI; frozen requested/catalog identity is gpt-6.1-sol Medium.']}
    s.runtime.write(s.ROOT/'evals/retrieval_optimization_results.v2.json',data,replace=True)
    lines=['# Retrieval optimization — resumed M2-06','',f'2026-10-08. **Status: {status}. {data["completed_configurations"]}/31 configurations complete.**','']
    if error:lines+=['Execution stopped at the documented gate: '+error,'']
    lines+=['Gold, original references and V3 scoring are unchanged. The proposed Qwen runtime retains explicit CPU isolation; context capacity is 2048 and batch/ubatch 1024 to reduce memory. Code checks exact model-input lengths before embedding and refuses overflow. A failed early preflight does not verify the input audit or runtime of later models.','',
        'The runner implements the frozen A → B → C sequence, linear pooled top16 percentile thresholds, whole-passage packing, exact-context cache reuse, exclusive execution and checked resume. A stage choice conservatively protects every covered requirement and every misleading/conflict/geography finding per case; unresolved or material tradeoffs stop advancement.','',
        '## All planned configurations','',
        '| Configuration | Model | k | Threshold | Packing | Retrieved / judged | Status | Micro25 / macro25 / complete25 |','|---|---|---:|---|---|---|---|---|']
    for row in records:
        c=row['configuration'];quality=row['full25']
        metrics='unavailable' if quality is None else f'{quality["micro_coverage"]} / {quality["macro_coverage"]} / {quality["complete_cases"]}'
        lines.append(f'| {c["id"]} | {c.get("model") or "pending stage choice"} | {c.get("k")} | {c.get("threshold_name",c.get("threshold"))} | {c["packing"]} | {row["retrieved_cases"]} / {row["judged_cases"]} | {row["status"]} | {metrics} |')
    lines+=['','The machine-readable results retain the legacy15 slice separately, all safety/relevance flags, partial reviewed decisions, token lists, resource measurements and gap results. Incomplete runs have no final ranking or recommended winner. Historical B8 was 34/51 and 7/13 on the original 15 cases; no 25-case or changed-scorer aggregate is treated as a controlled historical improvement.','',
        '## Resources and judging','']
    if preflight:
        lines += [f'Technical preflight passed: **{preflight["passed"]}**. Existing sealed regression cache checks: {preflight["cached_regression_checks"]}; fresh preflight judge calls: 0.','']
        for result in preflight['results']:
            resources=result['resources']
            lines += [f'- {result["model"]}: pass={result["success"]}; {resources["elapsed_seconds"]:.2f} s; simultaneous process-tree RSS {resources["peak_process_tree_rss_bytes"]/1e9:.3f} GB; minimum host available RAM {resources["minimum_available_ram_bytes"]/1e6:.1f} MB.']
        lines+=['','Operational limits were fixed before quality results: 256 MiB available-RAM reserve and 4 GiB process-tree RSS cap. Models run sequentially in separate workers. Measurements are sampled every 100 ms; they do not establish mobile feasibility.','']
    usage=data['consumption']
    lines += [f'Codex judge: {usage["actual_calls"]} actual calls, {usage["successful_calls"]} successful, {usage["cache_hits"]} experiment cache hits, {usage["unknown_usage_calls"]} calls with unknown usage. Tokens: `{json.dumps(usage["usage"])}`. Sum call time: {usage["sum_call_seconds"]:.2f} s. ChatGPT subscription only; paid API calls: 0.','',
        '## Recommendation and review','']
    if data['recommendation']:lines+=[f'Provisional retrieval recommendation: `{json.dumps(data["recommendation"])}`. Source/safety review remains a required final report check; no production implementation or final owner selection is performed.']
    else:lines+=['No retrieval winner is recommended from incomplete or blocked results. Resolve the concrete blocker before continuing the frozen plan; do not change gold, judge or parameters based on these observations.']
    lines+=['','Raw contexts, judge input/output, sources, vectors and worker logs remain ignored under `knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/`. Public artifacts contain configuration definitions, hashes and summaries. Original preflight/stability reports remain historical records. No holdout, answer generation, new source or production change was performed.']
    (s.ROOT/'evals/retrieval_optimization_report.v2.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    return data
