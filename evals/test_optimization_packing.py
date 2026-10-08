"""Whole-passage budgets, geography and runtime stop gates; no inference."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run_retrieval_optimization_v1 as r


def parent(identity,text,section='Root / Procedure',jurisdiction='general'):
    return r.KnowledgeItem(id=identity,text=text,title='Synthetic',source_name='Synthetic',source_url='synthetic://source',
               license='synthetic',language='en',topic='drill',section=section,document_id='synthetic',
               metadata={'jurisdiction':jurisdiction,'is_location_specific':jurisdiction!='general'})


class Counter:
    def count(self,text):return len(text),'synthetic-token-key'


class PackingTests(unittest.TestCase):
    def setUp(self):self.case={'question':'Synthetic question','jurisdiction':'NZ'}

    def test_p2_preserves_whole_parent_and_skips_oversized_parent(self):
        a=parent('a','x'*3000);b=parent('b','short instruction')
        seeds=[r.RetrievedKnowledgeItem(a,.9),r.RetrievedKnowledgeItem(b,.8)]
        rows,packets,trace=r.pack(self.case,seeds,[a,b],'P2',Counter(),2000)
        self.assertEqual([p.item.id for p in rows],['b']);self.assertEqual(trace[0]['status'],'over_budget')
        self.assertEqual(rows[0].item.text,'short instruction')

    def test_p1_uses_explicit_case_jurisdiction(self):
        nz=parent('nz','NZ instructions',jurisdiction='NZ');no=parent('no','Norwegian instructions',jurisdiction='NO')
        rows,_,_=r.pack(self.case,[r.RetrievedKnowledgeItem(nz,.9)],[nz,no],'P1',Counter())
        self.assertEqual([p.item.id for p in rows],['nz'])

    def test_p3_long_branch_falls_back_without_losing_other_seeds(self):
        parents=[parent(str(n),'Instruction '+str(n)) for n in range(4)]
        seeds=[r.RetrievedKnowledgeItem(p,.9) for p in parents[:2]]
        rows,_,_=r.pack(self.case,seeds,parents,'P3',Counter())
        self.assertEqual([p.item.id for p in rows],['0','1'])

    def test_p3_preserves_small_instruction_packet_atomically(self):
        parents=[parent('condition','Only in this synthetic condition'),parent('action','Perform the synthetic action')]
        seed=[r.RetrievedKnowledgeItem(parents[1],.9)]
        rows,_,_=r.pack(self.case,seed,parents,'P3',Counter())
        self.assertEqual([p.item.id for p in rows],['condition','action'])
        rows,_,trace=r.pack(self.case,seed,parents,'P3',Counter(),1)
        self.assertEqual(rows,[]);self.assertEqual(trace[0]['status'],'over_budget')

    def test_failed_model_probe_prevents_freeze_before_retrieval(self):
        with tempfile.TemporaryDirectory(dir=r.s.runtime.LOCAL) as folder:
            base=Path(folder);run=base/'experiment'
            r.s.runtime.write(base/'regression/summary.json',{'passed':True})
            for name in ['minilm','gemma2','qwen3-q4']:
                r.s.runtime.write(base/'model-preflight'/name/'attempt-01/result.json',{'success':name!='qwen3-q4'})
            with patch.object(r,'BASE',base),patch.object(r,'RUN',run):
                with self.assertRaisesRegex(RuntimeError,'qwen3-q4'):r.freeze()
            self.assertFalse(run.exists())


if __name__=='__main__':unittest.main()
