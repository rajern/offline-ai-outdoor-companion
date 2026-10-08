"""Targeted behavior checks; no model calls, retrieval, or holdout access."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import retrieval_optimization_scoring as s


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev={c['id']:c for c in s.load_development()['cases']}
        cls.corpus=s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items']

    def test_cache_key_changes_for_input_and_every_identity_field(self):
        payload={'question':'q','requirements':[{'item':1,'requirement':'r'}],'blocks':[{'block':1,'text':'a'}]}
        identity=s.identity({'cli_version':'test','catalog_model':s.runtime.MODEL})
        original=s.cache_key(payload,identity)
        for name in identity:
            changed=deepcopy(identity);changed[name]='different'
            self.assertNotEqual(original,s.cache_key(payload,changed),name)
        for name in ['question','requirements','blocks']:
            changed=deepcopy(payload);changed[name]='different'
            self.assertNotEqual(original,s.cache_key(changed,identity),name)
        self.assertEqual(original,s.cache_key(dict(reversed(list(payload.items()))),identity))

    def test_disabled_route_does_not_change_original_certificates(self):
        before=s.runtime.legacy.sha(s.CERTIFICATES)
        legacy=s.runtime.read(s.CERTIFICATES)
        corrected=s.rules()
        self.assertEqual(len(corrected['rules']['case-08'][0]['alternatives']),len(legacy['rules']['case-08'][0]['alternatives'])-1)
        self.assertEqual(before,s.runtime.legacy.sha(s.CERTIFICATES))

    def test_adjudication_exact_context_only_and_original_preserved(self):
        ref={'items':[{'covered':True}],'irrelevant':[],'potentially_misleading':[]}
        rec=s.runtime.read(s.ADJUDICATION)['records'][0]
        result=s.adjudicated_reference('case-08',rec['configuration'],rec['context_sha256'],ref)
        self.assertFalse(result['items'][0]['covered'])
        self.assertTrue(ref['items'][0]['covered'])
        self.assertEqual(ref,s.adjudicated_reference('case-08',rec['configuration'],'different',ref))

    def test_unknown_and_gap_never_earn_a_complete_pass(self):
        gap={'case_id':'case-25','coverage':{'gap':True,'total':0,'covered':0,'coverage':None,'complete_pass':False},
             'decisions':[],'requires_review':False,'flags':dict.fromkeys(['irrelevant','potentially_misleading','contradictory','jurisdiction_leakage'],False)}
        result=s.aggregate([gap]);self.assertEqual(result['complete_cases'],0);self.assertIsNone(result['micro_coverage'])
        unknown=deepcopy(gap);unknown.update(case_id='case-01',decisions=['uncertain'],requires_review=True)
        unknown['coverage'].update(gap=False,total=1,complete_pass=None)
        result=s.aggregate([unknown]);self.assertFalse(result['eligible_for_selection']);self.assertIsNone(result['micro_coverage']);self.assertEqual(result['uncertain_items'],1)

    def test_full_certificate_disagreement_blocks_selection(self):
        case=self.dev['case-08']
        parent=next(p for p in self.corpus if p['id']=='source-01-005') if any(p['id']=='source-01-005' for p in self.corpus) else self.corpus[0]
        row={'case_id':case['id'],'question':case['question'],'configuration':'synthetic','excerpts':[{'item':parent}],
             'context_tokens':100,'prompt_tokens':300,'context_budget':2000,'chunk_count':1,'section_count':1}
        inp=s.judge_input(case,row)
        answer={'case_id':case['id'],'items':[{'item':n,'decision':'not_covered','evidence':[],'missing_components':['missing'],'reason':'missing'} for n in range(1,len(inp['requirements'])+1)],
                'irrelevant':[],'potentially_misleading':[],'contradictory':[],'jurisdiction_leakage':[],'optional_observed':[],'requires_review':False}
        proof={'items':[{'decision':'covered'}]+[{'decision':'needs_review'}]*(len(inp['requirements'])-1),'provenance_issues':[]}
        with patch.object(s,'score_saved',return_value=proof):
            merged=s.merge(case,row,'unused',self.corpus,answer,s.rules())
        self.assertEqual(merged['certificate_judge_disagreement'],[1]);self.assertIsNone(merged['coverage']['coverage']);self.assertFalse(merged['eligible_for_selection'])

    def test_adapter_removes_hidden_configuration_and_expected_result(self):
        case=self.dev['case-25'];row={'case_id':case['id'],'question':case['question'],'configuration':'SECRET','excerpts':[],'rank':9,'score':.99}
        inp=s.judge_input(case,row)
        for key in ['configuration','rank','score','expected_result','must_have_evidence']:
            self.assertNotIn(key,inp)
        self.assertNotIn('SECRET',json.dumps(inp))

    def test_cache_reuses_call_and_detects_tampering(self):
        payload={'case_id':'synthetic','requirements':[],'blocks':[]}
        pre={'cli_version':'test','catalog_model':s.runtime.MODEL}
        ident=s.identity(pre)
        answer={'case_id':'synthetic','items':[],'irrelevant':[],'potentially_misleading':[],'contradictory':[],'jurisdiction_leakage':[],'optional_observed':[],'requires_review':False}
        usage={'input_tokens':10,'output_tokens':5,'total_tokens':15}
        def fake(directory,meta,pre):
            out=directory/'results/context-01';out.mkdir(parents=True)
            record={'success':True,'usage':usage,'input_sha256':meta['input_sha256'],'elapsed_seconds':1}
            for name,value in [('record.json',record),('answer.json',answer),('intent.json',meta),('command.json',{'test':True})]:s.runtime.write(out/name,value)
            events=[{'type':'item.completed','item':{'type':'agent_message','text':json.dumps(answer)}},{'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':5}}]
            (out/'stdout.jsonl').write_text('\n'.join(json.dumps(e) for e in events),encoding='utf-8')
            (out/'stderr.txt').write_text('',encoding='utf-8')
            return record
        with tempfile.TemporaryDirectory(dir=s.runtime.LOCAL) as folder,patch.object(s.runtime,'execute',side_effect=fake) as call:
            cache=Path(folder)
            first=s.judge(payload,pre,ident,cache=cache);second=s.judge(payload,pre,ident,cache=cache)
            self.assertEqual(call.call_count,1);self.assertFalse(first['cache_hit']);self.assertTrue(second['cache_hit']);self.assertEqual(second['calls'],0)
            path=cache/first['cache_key']/'results/context-01/record.json'
            changed=s.runtime.read(path);changed['elapsed_seconds']=2;s.runtime.write(path,changed,replace=True)
            with self.assertRaisesRegex(RuntimeError,'changed'):s.judge(payload,pre,ident,cache=cache)


if __name__=='__main__':unittest.main()
