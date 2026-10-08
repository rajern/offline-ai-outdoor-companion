"""Synthetic subprocesses only; never invoke Codex or OpenAI APIs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import codex_judge_runtime as r
import retrieval_judge_validation as v


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=r.LOCAL)
        self.base = Path(self.temp.name)
        self.schema = r.read(r.ROOT/'evals/retrieval_judge_output.schema.v2.json')
        self.inp = {'case_id':'synthetic','requirements':[{'item':1,'requirement':'Close the blue box.'}],
                    'blocks':[{'block':1,'text':'Close the blue box.'}]}
        self.answer = {'case_id':'synthetic','items':[{'item':1,'decision':'covered',
                       'evidence':[{'block':1,'quote':'Close the blue box.'}],
                       'missing_components':[],'reason':'The complete action is present.'}],
                       'irrelevant':[],'potentially_misleading':[],'contradictory':[],
                       'jurisdiction_leakage':[],'optional_observed':[],'requires_review':False}
        self.meta = {'context_id':'context-01','case_id':'synthetic','input_sha256':'synthetic',
                     'expected_result':'supported_context'}

    def tearDown(self):
        self.temp.cleanup()

    def setup_run(self):
        r.write(self.base/'index.json',[self.meta])
        r.write(self.base/'inputs/context-01.json',self.inp)
        r.write(self.base/'schema.json',self.schema)
        (self.base/'prompt.md').write_text('Synthetic instructions',encoding='utf-8')
        return self.base

    def write_events(self, out, text=None, usage=None):
        out.mkdir(parents=True,exist_ok=True)
        r.write(out/'intent.json',{'context_id':'context-01','input_sha256':'synthetic'})
        events = [{'type':'item.completed','item':{'type':'agent_message','text':text or json.dumps(self.answer)}},
                  {'type':'turn.completed','usage':usage or {'input_tokens':10,'output_tokens':5,'reasoning_output_tokens':2}}]
        (out/'stdout.jsonl').write_text('\n'.join(json.dumps(e) for e in events)+'\n',encoding='utf-8')

    def child_lock(self, path, *, crash=False):
        code = "import sys; sys.path.insert(0, sys.argv[1]); import codex_judge_runtime as r; from pathlib import Path; import os\n"
        code += "try:\n with r.JudgeLock(Path(sys.argv[2])):\n  print('entered',flush=True)\n"
        if crash: code += "  os._exit(0)\n"
        code += "except r.WorkerBusy:\n print('busy',flush=True)\n"
        return subprocess.run([sys.executable,'-c',code,str(r.ROOT/'evals'),str(path)],capture_output=True,text=True,timeout=20)

    def test_cross_process_worker_cannot_enter_same_lock(self):
        lock = self.base/'worker.lock'
        with r.JudgeLock(lock):
            result = self.child_lock(lock)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),'busy')
        self.assertEqual(self.child_lock(lock).stdout.strip(),'entered')

    def test_kernel_releases_lock_when_worker_crashes(self):
        lock = self.base/'worker.lock'
        result = self.child_lock(lock,crash=True)
        self.assertEqual(result.returncode,0,result.stderr)
        with r.JudgeLock(lock):
            pass

    def test_contradiction_needs_real_quote_and_misleading_overlap(self):
        self.answer['contradictory']=[{'evidence':[{'block':1,'quote':'Close the blue box.'}], 'reason':'Fictional conflict.'}]
        self.assertIn('contradiction must also be potentially misleading with shared evidence',r.validate(self.answer,self.inp,self.schema))
        self.answer['potentially_misleading']=self.answer['contradictory'].copy()
        self.assertFalse(r.validate(self.answer,self.inp,self.schema))
        self.answer['contradictory'][0]['evidence'][0]['quote']='made-up quote'
        self.assertTrue(r.validate(self.answer,self.inp,self.schema))

    def test_unknown_and_empty_gap_never_produce_complete_pass(self):
        self.answer['items'][0]['decision']='uncertain'
        self.answer['requires_review']=True
        self.assertIsNone(r.coverage(self.answer,self.inp,'supported_context')['coverage'])
        self.inp['requirements']=[]
        self.answer['items']=[]
        self.answer['requires_review']=False
        score=r.coverage(self.answer,self.inp,'insufficient_coverage')
        self.assertIsNone(score['coverage'])
        self.assertFalse(score['complete_pass'])

    def test_all_completed_turn_usage_is_counted(self):
        path=self.base/'stdout.jsonl'
        path.write_text('\n'.join(json.dumps({'type':'turn.completed','usage':{'input_tokens':n,'output_tokens':2}}) for n in [3,7]),encoding='utf-8')
        _,bad,usage=r.events_and_usage(path)
        self.assertEqual(bad,0)
        self.assertEqual(usage,{'input_tokens':10,'output_tokens':4,'total_tokens':14})

    def test_recover_completed_output_without_inference(self):
        self.setup_run()
        out=self.base/'results/context-01'
        self.write_events(out)
        active=self.base/'active.json'
        r.write(active,{'state':'in_flight','run_dir':str(self.base),'context_id':'context-01'})
        with patch.object(r.subprocess,'Popen') as process:
            r.recover_active(active)
            process.assert_not_called()
        record=r.read(out/'record.json')
        self.assertTrue(record['success'])
        self.assertTrue(record['recovered_without_call'])
        self.assertEqual(record['usage']['total_tokens'],15)
        self.assertIsNone(record['elapsed_seconds'])

    def test_existing_answer_recovery_never_overwrites(self):
        self.setup_run()
        out=self.base/'results/context-01'
        self.write_events(out)
        r.write(out/'answer.json',self.answer)
        self.assertTrue(r.finalize(self.base,self.meta,recovered=True)['success'])

    def test_incomplete_call_blocks_resume_without_retry(self):
        self.setup_run()
        out=self.base/'results/context-01'
        out.mkdir(parents=True)
        r.write(out/'intent.json',{'context_id':'context-01'})
        (out/'stdout.jsonl').write_text('{"type":"thread.started"}\n',encoding='utf-8')
        active=self.base/'active.json'
        r.write(active,{'state':'in_flight','run_dir':str(self.base),'context_id':'context-01'})
        with patch.object(r.subprocess,'Popen') as process:
            with self.assertRaises(RuntimeError): r.recover_active(active)
            process.assert_not_called()
        self.assertEqual(r.read(active)['state'],'in_flight')

    def test_invalid_answer_preserves_usage_and_cannot_be_retried(self):
        self.setup_run()
        out=self.base/'results/context-01'
        self.write_events(out,text='invalid json')
        record=r.finalize(self.base,self.meta,returncode=0,elapsed=1)
        self.assertFalse(record['success'])
        self.assertEqual(record['usage']['total_tokens'],15)
        with patch.object(r.subprocess,'Popen') as process:
            self.assertEqual(r.execute(self.base,self.meta,{}),record)
            process.assert_not_called()

    def test_tool_event_invalidates_result(self):
        self.setup_run()
        out=self.base/'results/context-01'
        self.write_events(out)
        with (out/'stdout.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps({'type':'item.completed','item':{'type':'command_execution'}})+'\n')
        self.assertIn('tool/event isolation violation',r.finalize(self.base,self.meta)['validation_errors'])

    def test_real_synthetic_subprocess_logged_then_skipped(self):
        self.setup_run()
        code="import sys,json; json.load(sys.stdin); print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':sys.argv[1]}})); print(json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':5}}))"
        command=[sys.executable,'-c',code,json.dumps(self.answer)]
        pre={'cli':'unused','cli_version':'synthetic','authentication':'chatgpt_subscription'}
        active=self.base/'active.json'
        original_tempdir=tempfile.TemporaryDirectory
        with patch.object(r.legacy,'codex_command',return_value=command), patch.object(r.tempfile,'TemporaryDirectory',
                side_effect=lambda **kw:original_tempdir(dir=self.base,**kw)):
            record=r.execute(self.base,self.meta,pre,active_file=active)
        self.assertTrue(record['success'],record)
        self.assertTrue((self.base/'results/context-01/stdout.jsonl').exists())
        with patch.object(r.subprocess,'Popen') as process:
            self.assertEqual(r.execute(self.base,self.meta,pre,active_file=active),record)
            process.assert_not_called()

    def test_environment_and_command_preserve_subscription_isolation(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'synthetic','CODEX_API_KEY':'synthetic'}):
            env=r.legacy.codex_environment()
        self.assertNotIn('OPENAI_API_KEY',env)
        self.assertNotIn('CODEX_API_KEY',env)
        command=r.legacy.codex_command('unused',self.base,{'codex_model':r.MODEL},output=False)
        for flag in ['forced_login_method="chatgpt"','model_reasoning_effort="medium"','features.shell_tool=false']:
            self.assertIn(flag,command)
        self.assertNotIn('--output-last-message',command)

    def test_no_model_call_when_all_attempts_are_recorded(self):
        self.setup_run()
        r.write(self.base/'results/context-01/record.json',{'success':False})
        with patch.object(v,'verify'),patch.object(r,'JudgeLock'),patch.object(r,'ACTIVE',self.base/'absent'),patch.object(r,'preflight') as pre:
            v.run(self.base)
            pre.assert_not_called()

    def test_stage_expectations_stay_outside_judge_input(self):
        data=r.read(r.ROOT/'evals/retrieval_judge_stress.v2.json')
        self.assertEqual(len(data['cases']),15)
        self.assertEqual(len(data['repeat_test_ids']),3)
        for case in data['cases']:
            inp=case['input']
            for secret in ['expected','expected_result','configuration','purpose','test_id','reference']:
                self.assertNotIn(secret,inp)


if __name__=='__main__': unittest.main()
