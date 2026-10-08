"""Phase boundaries, accounting, safety tradeoffs and resume checks; no inference."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import run_retrieval_optimization_v1 as r
from optimization_resources import Resources,RAM_RESERVE,RSS_LIMIT,validate_vectors


class OrchestrationTests(unittest.TestCase):
    def test_thresholds_pool_allowed_top16_with_linear_percentiles(self):
        rows=[{'candidates_top16':[{'score':v} for v in [.1,.3]]},
              {'candidates_top16':[{'score':v} for v in [.5,.9]]}]
        result=r.threshold_values(rows)
        self.assertAlmostEqual(result['p10'],.16)
        self.assertAlmostEqual(result['p50'],.4)
        self.assertAlmostEqual(result['p70'],.54)

    def test_invalid_threshold_distribution_stops(self):
        for rows in [[],[{'candidates_top16':[{'score':float('nan')}]}]]:
            with self.assertRaises(ValueError):r.threshold_values(rows)

    def test_material_per_case_tradeoff_stops_before_stage_choice(self):
        records=[]
        for cid,decisions in [('A-one',['covered','not_covered']),('A-two',['not_covered','covered'])]:
            records.append({'configuration':{'id':cid},'full25':{'eligible_for_selection':True},
                'scores':[{'case_id':'case-01','decisions':decisions,'flags':{
                    'potentially_misleading':False,'contradictory':False,'jurisdiction_leakage':False}}]})
        with patch.object(r.s.runtime,'read',side_effect=records):
            with self.assertRaisesRegex(RuntimeError,'tradeoffs'):r.choose_stage(['A-one','A-two'])

    def test_unresolved_review_never_selects_winner(self):
        with patch.object(r.s.runtime,'read',return_value={'full25':{'eligible_for_selection':False}}):
            with self.assertRaisesRegex(RuntimeError,'reviews'):r.choose_stage(['A-one'])

    def test_phase_b_resolves_only_frozen_model_threshold_and_p2(self):
        records={'plan.json':{'phase_a':[],'phase_b':[{'id':'B-k8-p30','k':8,'threshold_name':'p30','packing':'P2'}],'phase_c':[]},
            'choice-A.json':{'configuration':{'model':'qwen3-q4'}},'thresholds.json':{'values':{'p30':.23}}}
        with patch.object(r.s.runtime,'read',side_effect=lambda p:records[p.name]):
            value=r.configuration('B-k8-p30')
            self.assertEqual((value['model'],value['k'],value['threshold'],value['packing']),('qwen3-q4',8,.23,'P2'))
            with self.assertRaises(ValueError):r.configuration('unplanned')

    def test_phase_c_carries_chosen_model_k_threshold_without_grid(self):
        records={'plan.json':{'phase_a':[],'phase_b':[],'phase_c':[{'id':'C-P3','packing':'P3'}]},
            'choice-A.json':{'configuration':{'model':'gemma2'}},
            'choice-B.json':{'configuration':{'model':'gemma2','k':5,'threshold':None}}}
        with patch.object(r.s.runtime,'read',side_effect=lambda p:records[p.name]):
            self.assertEqual(r.configuration('C-P3'),{'id':'C-P3','packing':'P3','model':'gemma2','k':5,'threshold':None})

    def test_sampled_memory_violation_stays_blocking_after_recovery(self):
        resources=Resources();resources.samples=[(100,RAM_RESERVE-1),(100,RAM_RESERVE+1)]
        with self.assertRaisesRegex(RuntimeError,'Resource guard'):resources.check()
        resources.samples=[(RSS_LIMIT+1,RAM_RESERVE+1)]
        with self.assertRaises(RuntimeError):resources.check()

    def test_index_shapes_and_normalization_are_checked(self):
        validate_vectors(np.eye(3),np.eye(3),3,3)
        with self.assertRaises(ValueError):validate_vectors(np.eye(3),np.eye(2),3,2)
        with self.assertRaises(ValueError):validate_vectors(np.zeros((3,3)),np.eye(3),3,3)

    def test_token_cache_rejects_modified_tokenizer_output(self):
        with tempfile.TemporaryDirectory(dir=r.s.runtime.LOCAL) as folder:
            base=Path(folder);counter=r.TokenCounter(base);text='Synthetic token input';key=r.s.runtime.legacy.text_sha(text)
            target=base/key;target.mkdir();(target/'input.txt').write_text(text,encoding='utf-8')
            (target/'stdout.txt').write_text('[1,2]',encoding='utf-8')
            r.s.runtime.write(target/'count.json',{'tokens':2,'stdout_sha256':r.file_hash(target/'stdout.txt')})
            self.assertEqual(counter.count(text),(2,key))
            (target/'stdout.txt').write_text('[1,3]',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'hash'):counter.count(text)

    def test_technical_retry_cannot_change_identities_after_experiment_freeze(self):
        with tempfile.TemporaryDirectory(dir=r.s.runtime.LOCAL) as folder:
            base=Path(folder);run=base/'experiment';run.mkdir()
            path=base/'technical-preflight/summary.json'
            record={'passed':False,'code_hashes':{},'failure':'memory reserve'}
            r.s.runtime.write(path,record)
            with patch.object(r,'BASE',base),patch.object(r,'RUN',run),patch.object(r,'CODE',[]), \
                 patch('run_judge_regression_v3.verify'):
                with self.assertRaisesRegex(RuntimeError,'after the experiment freeze'):r.technical(retry=True)
            self.assertEqual(r.s.runtime.read(path),record)

    def test_explicit_prefreeze_retry_preserves_previous_failure(self):
        with tempfile.TemporaryDirectory(dir=r.s.runtime.LOCAL) as folder:
            base=Path(folder);run=base/'experiment'
            old={'passed':False,'code_hashes':{},'failure':'memory reserve'}
            r.s.runtime.write(base/'technical-preflight/summary.json',old)
            r.s.runtime.write(base/'regression/judge-identity.json',{})
            r.s.runtime.write(base/'regression/plan.json',[])
            def fake_worker(command,model):
                r.s.runtime.write(base/'technical-preflight'/model/'attempt-01/result.json',{'model':model,'success':True})
            with patch.object(r,'BASE',base),patch.object(r,'RUN',run),patch.object(r,'CODE',[]), \
                 patch('run_judge_regression_v3.verify'),patch.object(r.s.runtime,'preflight',return_value={}), \
                 patch.object(r.s,'identity',return_value={}),patch.object(r.s.runtime,'recover_active'), \
                 patch.object(r,'worker',side_effect=fake_worker):
                r.technical(retry=True)
            history=list((base/'technical-preflight/summary-history').glob('*.json'))
            self.assertEqual(len(history),1)
            self.assertEqual(r.s.runtime.read(history[0]),old)
            self.assertTrue(r.s.runtime.read(base/'technical-preflight/summary.json')['passed'])
            self.assertFalse(run.exists())

    def test_full_driver_runs_exactly_31_and_freezes_threshold_before_phase_b(self):
        with tempfile.TemporaryDirectory(dir=r.s.runtime.LOCAL) as folder:
            base=Path(folder);run=base/'experiment';calls=[]
            plan={'phase_a':[{'id':'A-'+m,'model':m,'k':8,'threshold':None,'packing':'P2'} for m in ['minilm','gemma2','qwen3-q4']],
                'phase_b':[{'id':f'B-k{k}-{t}','k':k,'threshold_name':t,'packing':'P2'} for k in [3,5,8,12,16] for t in ['none','p10','p30','p50','p70']],
                'phase_c':[{'id':'C-'+p,'packing':p} for p in ['P1','P2','P3']]}
            def freeze():
                run.mkdir();r.s.runtime.write(run/'plan.json',plan)
            def fake_worker(command,model=None,config_id=None):
                calls.append((command,model,config_id))
                if config_id and config_id.startswith('B-'):self.assertTrue((run/'thresholds.json').exists())
                if command=='retrieve':r.s.runtime.write(run/'configurations'/config_id/'retrieved-all.json',[])
            def choice(stage,ids):
                return {'id':ids[0],'model':'minilm','k':8,'threshold':None,'packing':'P2'}
            with patch.object(r,'BASE',base),patch.object(r,'RUN',run),patch.object(r,'technical'), \
                 patch.object(r,'freeze',side_effect=freeze),patch.object(r,'verify'), \
                 patch.object(r,'worker',side_effect=fake_worker),patch.object(r,'stage_choice',side_effect=choice), \
                 patch.object(r,'verify_rows',return_value=[{'candidates_top16':[{'score':i/20} for i in range(16)]}]*25):
                r.run_all()
            retrieved=[c[2] for c in calls if c[0]=='retrieve'];scored=[c[2] for c in calls if c[0]=='score']
            self.assertEqual(retrieved,scored)
            self.assertEqual(len(retrieved),31)
            self.assertEqual(len(set(retrieved)),31)
            self.assertEqual([sum(c.startswith(prefix) for c in retrieved) for prefix in ['A-','B-','C-']],[3,25,3])


if __name__=='__main__':unittest.main()
