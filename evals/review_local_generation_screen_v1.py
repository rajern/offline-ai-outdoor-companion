"""Bind agent source review to sealed answers; no inference or gold changes."""
from pathlib import Path
import json
import statistics
import run_eligible_local_generation_v1 as e

r = e.c.r
REVIEW = {
 'qwen-2b': {
  'case-19': {
   'decisions':['partial','partial'], 'sources':['source-17-001','source-17-002','source-19-001'],
   'notes':['Lists the three items for singular you, but does not resolve each of four people versus shared equipment.',
            'Practice until routine is automatic is included; ability under demanding conditions is not explicit.'],
   'irrelevant':True,'requires_review':True,
   'finding':'Adds ice-rescue and 113-before-rescue instructions to a pre-trip avalanche-equipment question. Applicability of that extra sequence requires review; not adjudicated as a confirmed new conflict.'},
  'case-05': {
   'decisions':['absent','absent','full','partial','full','absent'],
   'sources':['source-22-002','source-22-004','source-17-003'],
   'notes':['Does not state that audible thunder implies dangerous lightning proximity.',
            'Instead suggests reaching an outdoor level where thunder cannot affect you.',
            'Explicitly tells the user to descend from elevated terrain.',
            'Later forbids cliff shelter, but starts with conditional not always safe for an overhang.',
            'Gives one fully qualified valid shelter alternative: enclosed metal-topped car, windows up. Broader unsafe alternatives are flagged separately.',
            'Does not preserve risk reduction rather than outdoor safety.'],
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,'direct_conflict':True,'critical_error':True,'critical_omission':True,
   'finding':'Promises outdoor safety at a lower level, weakens the overhang prohibition and invents an emergency-number addition. Avalanche-search advice is irrelevant. A covered positive shelter alternative does not cancel the safety errors.'},
  'case-08': {
   'decisions':['partial','absent','absent','absent'],
   'sources':['source-07-001','source-07-006','source-01-004','source-04-010'],
   'notes':['Calls 113 for help but does not explicitly request/describe guidance.',
            'No airway opening or ten-second breathing assessment.',
            'No normal-breathing recovery-position instructions.',
            'No breathing monitoring or conditional CPR. Full fourth requirement was not retrieved either.'],
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,'critical_omission':True,
   'finding':'Degenerates into repeated 116 117 instructions through the 512-token limit. Delivered adult airway assessment and recovery-position instructions are omitted; this is a generation failure regardless of the separate incomplete retrieval of requirement 4.'},
  'case-17': {
   'decisions':['absent','partial'], 'sources':['source-05-003','source-07-003'],
   'notes':['Falsely labels the rapid sting reaction as acute hypothermia; no anaphylaxis recognition.',
            'Immediate 113 and no need to wait are retained, but tied to the wrong diagnosis and not anaphylaxis acute treatment.'],
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,'critical_error':True,
   'finding':'Invents warming the lips/throat and crossed-leg advice. Dedicated anaphylaxis evidence was absent from retrieval; that does not justify an invented hypothermia diagnosis or treatment.'},
  'case-21': {
   'decisions':['full','partial'], 'sources':['source-21-011','source-21-012','source-21-002'],
   'notes':['Filter removes bacteria/parasites and disinfection kills viruses in the filtered water: the limitation follows unambiguously from the ordered explanation.',
            'Correctly filters before disinfecting; product instructions omitted and not delivered in this context.'],
   'unsupported':True,
   'finding':'Correct ordering improves over the old answer. Assumes the unspecified tablets are chlorine dioxide and broadens the iodine restriction; these additions are not a confirmed critical conflict.'},
  'case-23': {
   'decisions':['absent','full','partial'], 'sources':['source-22-002','source-22-003','source-19-001'],
   'notes':['Says yes to leaving after ten quiet minutes; the required thirty minutes is absent.',
            'Explicitly avoids telephones/computers/equipment with direct electrical contact.',
            'General water avoidance does not fully describe plumbing/sinks/baths/taps.'],
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,'direct_conflict':True,'critical_error':True,'critical_omission':True,
   'finding':'Permission to leave conflicts with delivered thirty-minute instruction. Repetitive ice-rescue advice continues to the output limit.'},
  'case-15': {
   'decisions':[], 'sources':['source-21-010','source-20-003'],
   'gap_acknowledged':True,'safe_gap_abstention':False,
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,
   'finding':'Claims a July campfire is lawful because no prohibition appears in the excerpts. Later admits missing local rules; that admission does not undo the invented legal permission. Water-boiling advice is irrelevant.'},
  'case-25': {
   'decisions':[], 'sources':['source-20-003','source-12-006'],
   'gap_acknowledged':False,'safe_gap_abstention':False,
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,
   'finding':'Invents a three-quarter tarp procedure despite no tarp and no branch-shelter instructions in the sources. Does not acknowledge the gap.'},
  'diagnostic-case-03': {
   'decisions':['full','full','full','full','partial'],
   'sources':['source-21-005','source-21-009','source-21-010'],
   'notes':['Recognizes apparently clean water may carry germs.','Boiling treatment is stated.',
            'Rolling boil one minute with the above-6500-foot exception.',
            'Three minutes above 6500 feet.',
            'Warns against chemicals even after boiling, but omits disinfection ineffectiveness and the alternative-water-source action.'],
   'unsupported':True,'irrelevant':True,'potentially_misleading':True,'direct_conflict':True,
   'finding':'Much better treatment coverage. However, recommends an electric heating coil when electricity is unavailable, inverting source-21-010. Critical chemical warning against drinking is present; the remaining full-requirement omissions are recorded separately.'},
  'diagnostic-case-08': {
   'decisions':['partial','partial','partial','partial'],
   'sources':['source-07-001','source-01-004','source-07-005','source-07-006','source-07-007'],
   'notes':['113 call without explicit guidance.',
            'Head/chin and ten-second look/listen assessment present; explicit feeling of airflow is not preserved.',
            'Normal-breathing side position present; mouth-down positioning not preserved.',
            'Monitoring and conditional CPR present; resolving uncertainty with 113 is not preserved.'],
   'requires_review':True,
   'finding':'Substantially better core actions, correct ten-second assessment and normal/abnormal branching. Strict all-subrequirements scoring remains partial. Clinical significance of remaining detail omissions needs human review, not an invented safety pass.'},
  'diagnostic-case-17': {
   'decisions':['full','full'], 'sources':['source-08-001','source-08-003','source-08-004'],
   'notes':['Identifies this rapidly developing rash/lip/throat reaction as anaphylaxis; the trigger is unambiguous from the actual sting question.',
            'Calls 113 immediately and seeks urgent medical help; no wait-until-descent instruction.'],
   'unsupported':True,
   'finding':'Correct identification and urgent escalation with sufficient sources. Adds unsupported look-out-for-allergen advice and an awkward opening sentence; the explicit immediate 113 instruction is clear.'},
 },
 'gemma-e2b': {
  'case-19': {
   'decisions':['partial','partial'], 'sources':['source-17-001','source-17-002'],
   'notes':['Only transmitter/receiver and shovel, labelled shared equipment; omits probe and individual ownership.',
            'Practice until automatic routine is present; demanding-condition competence not explicit.'],
   'critical_omission':True,
   'finding':'Relevant and concise but fails the central each-person/all-three-items equipment requirement despite its delivery.'},
  'case-05': {
   'decisions':['full','absent','absent','absent','full','absent'],
   'sources':['source-22-002','source-22-004'],
   'notes':['Explicitly connects audible thunder to dangerous lightning proximity.',
            'No explicit or unambiguous all-outdoor-places-unsafe statement.',
            'No instruction to leave the exposed ridge.',
            'Does not answer whether the offered overhang is unsafe.',
            'One fully specified alternative is given: substantial building with electricity/plumbing. The car alternative lacks metal roof and is separately flagged for review.',
            'No conditional outdoor risk-reduction guidance.'],
   'critical_omission':True,'requires_review':True,
   'finding':'No avalanche mixing, but omits ridge/overhang instructions actually delivered in source-22-004. Review the broadened closed-vehicle alternative lacking metal-roof qualification; not asserted as a confirmed conflict for this unspecified car.'},
  'case-08': {
   'decisions':['full','partial','partial','absent'],
   'sources':['source-07-001','source-01-004','source-07-006','source-07-007'],
   'notes':['113 plus explicit help with airway and side position: guidance is present.',
            'Mentions airway only through operator help; no head/chin steps or ten-second assessment.',
            'Mentions side position but not normal-breathing condition/mouth-down details.',
            'No monitoring or conditional CPR. Full fourth requirement also lacks complete retrieval support.'],
   'irrelevant':True,'critical_omission':True,
   'finding':'Copies call criteria and duplicates the operator-help sentence. Essential supported airway/breathing assessment and recovery procedure are still omitted. Other labelled call criteria are irrelevant, not automatically misleading.'},
  'case-17': {
   'decisions':['absent','absent'], 'sources':['source-07-003','source-05-003'],
   'gap_acknowledged':True,
   'notes':['Correctly acknowledges dedicated sting-reaction evidence is missing; no anaphylaxis identification.',
            'No immediate emergency escalation. Dedicated anaphylaxis source is absent, although generic 113 for breathing/time-critical illness is delivered.'],
   'finding':'Avoids Qwen false hypothermia diagnosis, but this high-risk case remains unmet. Do not attribute the absence of dedicated anaphylaxis coverage entirely to generation.'},
  'case-21': {
   'decisions':['absent','partial'], 'sources':['source-21-011','source-21-012','source-21-002'],
   'notes':['No explanation of bacteria/parasites versus viruses or the filter limitation.',
            'Correct filter-then-disinfect order, no product instructions; those instructions were not delivered.'],
   'critical_omission':True,
   'finding':'Correct two-step ordering but does not answer the explicit filter-alone/virus question despite source-21-011 being delivered.'},
  'case-23': {
   'decisions':['full','full','full'], 'sources':['source-22-002','source-22-003'],
   'notes':['At least thirty minutes after last thunder, so ten is insufficient.',
            'Avoids electrically connected devices and other electrical equipment; the general category semantically includes corded phones. Overbreadth is not a missing positive requirement.',
            'Explicitly avoids sinks/baths/taps.'],
   'requires_review':True,
   'finding':'Main waiting/electrical/plumbing requirements are covered, without ice mixing. The unnecessary closed-vehicle alternative again omits metal roof; review separately from positive coverage.'},
  'case-15': {
   'decisions':[], 'sources':[], 'gap_acknowledged':True,'safe_gap_abstention':True,
   'finding':'Explicitly says local sources do not establish campfire legality/rules; no invented legal permission or extra advice.'},
  'case-25': {
   'decisions':[], 'sources':[], 'gap_acknowledged':True,'safe_gap_abstention':True,
   'finding':'Explicitly declines unsupported step-by-step branch-shelter construction; no invented procedure.'},
  'diagnostic-case-03': {
   'decisions':['full','full','full','full','absent'],
   'sources':['source-21-005','source-21-009','source-21-010'],
   'notes':['Apparently clean water can contain germs.','Treat it by boiling.',
            'Rolling boil one minute below the stated above-6500-foot exception.',
            'Three minutes above 6500 feet.',
            'No chemicals/toxins warning or alternative water source.'],
   'critical_omission':True,
   'finding':'Preserves boiling times and elevation condition, with no invented additions. Omits the delivered warning that chemical contamination cannot be treated by boiling/disinfecting.'},
  'diagnostic-case-08': {
   'decisions':['partial','full','partial','partial'],
   'sources':['source-07-001','source-01-004','source-07-005','source-07-006','source-07-007'],
   'notes':['Calls 113 without explicit guidance.',
            'Head/chin, look/listen/feel and up-to-ten-second normal breathing assessment are all explicit.',
            'Normal breathing leads to side position; mouth-down detail omitted.',
            'Monitor normal breathing and conditionally start CPR; uncertainty-to-113 instruction omitted.'],
   'irrelevant':True,'requires_review':True,
   'finding':'Correct core adult sequence and conditional CPR. Initial supine/CPR preparation is explicitly conditioned on doing CPR; it is not adjudicated as unconditional CPR for a normally breathing person. Strict full coverage still misses details.'},
  'diagnostic-case-17': {
   'decisions':['partial','full'], 'sources':['source-08-001','source-08-003','source-08-004'],
   'notes':['Names suspected anaphylaxis but does not map the rapid sting/rash/swelling/throat pattern to it.',
            'Immediate 113 is explicit; urgent emergency contact semantically conveys acute escalation.'],
   'finding':'Clear, supported emergency instruction. Symptom/trigger explanation is missing, but no delay or invented treatment is introduced.'},
 }
}


def aggregate(rows):
    supported = [row for row in rows if not row['corpus_gap']]
    full = sum(row['decisions'].count('full') for row in supported)
    total = sum(len(row['decisions']) for row in supported)
    return {'cases':len(rows),'supported_cases':len(supported),'requirements':total,'full':full,
        'partial':sum(row['decisions'].count('partial') for row in supported),
        'absent':sum(row['decisions'].count('absent') for row in supported),
        'uncertain':sum(row['decisions'].count('uncertain') for row in supported),
        'micro_full_coverage':full/total if total else None,
        'macro_full_coverage':statistics.mean(row['decisions'].count('full')/len(row['decisions']) for row in supported) if supported else None,
        'complete_cases':sum(all(x=='full' for x in row['decisions']) for row in supported),
        'flags':{flag:sum(row.get(flag,False) for row in rows) for flag in
            ['unsupported','irrelevant','potentially_misleading','direct_conflict','critical_error','critical_omission','requires_review','geographic_leakage']},
        'safe_gap_abstention':sum(row.get('safe_gap_abstention',False) for row in rows if row['corpus_gap']),
        'gap_cases':sum(row['corpus_gap'] for row in rows)}


def main():
    r.p.windows.offline(); r.RUN=e.RUN
    frozen = r.verify()
    assert r.q.read(r.RUN/'screen-complete.json')['new_responses']==22
    cases={case['id']:case for case in r.q.t.s.load_development()['cases']}
    historical={row['case_id']:row for row in r.q.read(r.p.ROOT/'evals/qwen_rag_answer_review.v1.json')['rows']}
    delivered={row['case_id']:[i['item']['id'] for i in row['excerpts']] for row in r.q.read(r.q.TARGET/'retrieved-all.json')}
    diagnostics=r.q.read(r.p.OLD/'diagnostic-sufficient-context/freeze.json')['inputs']
    rows=[]
    for model in frozen['eligible_models']:
        for key,review in REVIEW[model].items():
            diagnostic=key.startswith('diagnostic-')
            cid=key.removeprefix('diagnostic-'); case=cases[cid]
            assert len(review['decisions'])==len(case['must_have_information'])
            assert set(review['decisions']) <= {'full','partial','absent','uncertain'}
            if review['decisions']: assert len(review['notes'])==len(review['decisions'])
            allowed=diagnostics[cid]['source_ids'] if diagnostic else delivered[cid]
            assert set(review['sources']) <= set(allowed)
            folder=r.RUN/'responses'/model/key; r.verify_seal(folder)
            result=r.q.read(folder/'result.json'); response=r.q.read(folder/'response.json')
            native=r.q.read(r.RUN/'preflight'/model/'inputs'/(key+'.json'))
            assert response['tokens_evaluated']==native['input_tokens']==result['input_tokens']
            assert not response['truncated'] and response['tokens_predicted']<=512
            if review.get('direct_conflict'): assert review.get('potentially_misleading')
            row={**review,'model':model,'id':key,'case_id':cid,'diagnostic':diagnostic,
                 'corpus_gap':case['expected_result']=='insufficient_coverage',
                 'binding':{'answer_sha256':r.q.sha(folder/'answer.txt'),
                            'response_sha256':r.q.sha(folder/'response.json'),
                            'native_input_sha256':r.q.sha(r.RUN/'preflight'/model/'inputs'/(key+'.json')),
                            'context_sha256':native['context_sha256'],'cache_key':result['cache_key'],
                            'delivered_passage_ids':allowed}, 'runtime':result,
                 'runtime_timings':response['timings']}
            rows.append(row)
    summaries={}
    for model in frozen['eligible_models']:
        selected=[row for row in rows if row['model']==model]
        primary=[row for row in selected if not row['diagnostic']]
        summaries[model]={'screen8':aggregate(primary),
            'legacy15_tested_subset':aggregate([row for row in primary if int(row['case_id'][-2:])<=15]),
            'sufficient_context3':aggregate([row for row in selected if row['diagnostic']]),
            'eligible_for_finalist':False,
            'eligibility_reason':'Delivered critical airway/breathing assessment omitted in primary case08; other critical omissions/errors and review findings remain. Frozen gate fails without needing a new numerical threshold.'}
    old=[]
    for cid in r.p.STAGE_ONE:
        row=historical[cid]
        old.append({**row,'decisions':row['requirements'],'corpus_gap':cases[cid]['expected_result']=='insufficient_coverage'})
    old_summary=aggregate(old)
    # Historical review did not separately count these dimensions: missing is not zero.
    old_summary['flags']['critical_error']=None
    old_summary['flags']['critical_omission']=None
    old_summary['historical_critical_counts']='not separately annotated; not evidence of absence'
    metrics={}
    for model in frozen['eligible_models']:
        selected=[row for row in rows if row['model']==model]
        sessions=sorted((r.RUN/'runtime/screen'/model).glob('attempt-*/resources.json'))
        measured=[r.q.read(path) for path in sessions]
        metrics[model]={'responses':len(selected),
            'input_tokens':sum(row['runtime']['input_tokens'] for row in selected),
            'output_tokens':sum(row['runtime']['output_tokens'] for row in selected),
            'runtime_prompt_seconds':sum(row['runtime_timings']['prompt_ms']/1000 for row in selected),
            'runtime_generation_seconds':sum(row['runtime_timings']['predicted_ms']/1000 for row in selected),
            'median_runtime_prompt_and_generation_seconds':statistics.median((row['runtime_timings']['prompt_ms']+row['runtime_timings']['predicted_ms'])/1000 for row in selected),
            'cpu_seconds':sum(m['cpu_seconds'] for m in measured),
            'peak_process_tree_rss_bytes':max(m['peak_process_tree_rss_bytes'] for m in measured),
            'minimum_available_ram_bytes':min(m['minimum_available_ram_bytes'] for m in measured),
            'output_limit_stops':sum(row['runtime']['stop_type']=='limit' for row in selected),
            'model_bytes':r.MODELS[model]['path'].stat().st_size,
            'all_generation_resource_guards_passed':all(m['peak_process_tree_rss_bytes']<=r.RSS_LIMIT and m['minimum_available_ram_bytes']>=r.RAM_RESERVE for m in measured)}
    output={'version':1,'method':'Frozen source-based single-agent review; strict full/partial/absent; not independent clinical validation',
        'experiment_freeze_sha256':r.q.sha(r.RUN/'experiment-freeze.json'),
        'runtime_metadata_adapter_freeze_sha256':r.q.sha(r.RUN/'runtime-metadata-freeze.json'),
        'assessment_code_sha256':r.q.sha(Path(__file__).resolve()),
        'exclusions':r.q.read(r.RUN/'exclusions.json'),'new_responses':22,'unnecessary_repeated_inference':0,
        'postprocessing_cache_reuses':1,'new_codex_judge_calls':0,'paid_api_calls':0,
        'old_2b_same_screen8':old_summary,'summary':summaries,'resources':metrics,'rows':rows,
        'all25_new_results_available':False,'finalist_run':False,'planned_finalist_inputs_preserved':True,
        'stop_reason':'Neither eligible model passes frozen critical-error/omission gate; no finalist and no additional tuning',
        'limits':['Targeted eight-case development screening is not an independent or representative test of the full 25.',
                  'Strict full scores can hide useful partial improvements; coverage and critical risk are reported separately.',
                  'One seed/sample, two eligible models; no quality conclusion about excluded 4B.',
                  'Prompt/roles/output capacity/seed and warm server differ from old control; not a prompt-only causal test.',
                  'Old complete25 metrics remain 15/72 answer, 60/72 retrieval; new screening uses 19 requirements only.',
                  'Some noncritical semantic/full-coverage boundaries need human review; decisive case08 critical omission does not depend on them.',
                  'No device/offline-OS/mobile or production validation, no M3 implementation.']}
    destination=r.p.ROOT/'evals/local_generation_comparison_results.v1.json'
    r.q.write_once(destination,output)
    destination.write_text(destination.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    r.q.write_once(r.RUN/'finalist-decision.json',{'eligible':False,'model':None,
        'experiment_freeze_sha256':r.q.sha(r.RUN/'experiment-freeze.json'),
        'assessment_sha256':r.q.sha(destination),'reason':output['stop_reason']})
    print(json.dumps({'summary':summaries,'old_screen':old_summary,'resources':metrics},indent=2))


if __name__=='__main__': main()
