"""Decision-boundary diagnostics use set membership, order and unchanged tolerances."""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock,patch
import numpy as np
import diagnose_qwen_stability as d


class StabilityMetricsTests(unittest.TestCase):
    def test_inside_top_k_reorder_does_not_claim_membership_change(self):
        a=np.arange(24,0,-1,dtype=np.float32)[None,:]
        b=a.copy();b[0,0],b[0,1]=b[0,1],b[0,0]
        row=d.compare_scores(a,b)[0]
        self.assertTrue(row['order_changed'])
        for k in d.KS:
            self.assertTrue(row['top_k'][str(k)]['order_changed'])
            self.assertFalse(row['top_k'][str(k)]['membership_changed'])

    def test_boundary_crossing_records_both_passages_and_threshold_flips(self):
        a=np.arange(24,0,-1,dtype=np.float32)[None,:]
        b=a.copy();b[0,2],b[0,3]=b[0,3],b[0,2]
        value=d.compare_scores(a,b)[0]['top_k']['3']
        self.assertTrue(value['membership_changed'])
        self.assertEqual(value['entered_indices'],[3])
        self.assertEqual(value['left_indices'],[2])
        self.assertEqual(value['threshold_flip_indices'],[2,3])
        self.assertEqual(value['reference_boundary_gap'],1)

    def test_ties_have_stable_identity_order(self):
        a=np.zeros((1,24))
        self.assertEqual(d.ranking(a)[0].tolist(),list(range(24)))
        self.assertFalse(d.compare_scores(a,a)[0]['order_changed'])

    def test_small_vector_difference_can_fail_original_tolerance_without_rank_changes(self):
        docs=np.zeros((24,28),dtype=np.float32);docs[np.arange(24),np.arange(24)]=1
        q=np.zeros((4,28),dtype=np.float32);q[:,0]=1
        changed=q.copy();changed[0,24]=2e-5
        result=d.summarize([(docs,q),(docs,q),(docs,changed),(docs,changed)])
        self.assertFalse(result['all_pairs_original_tolerance_pass'])
        self.assertEqual(result['order_changes'],0)
        self.assertEqual(result['query_pair_count'],24)
        self.assertTrue(all(n==0 for n in result['top_k_membership_changes'].values()))

    def test_default_adapter_enforces_cpu_without_changing_model_or_pooling(self):
        process=MagicMock();process.poll.return_value=None
        response=MagicMock();response.__enter__.return_value.status=200
        with tempfile.TemporaryDirectory(dir=d.e.LOCAL) as folder,patch('socket.socket'), \
             patch.object(d.e.subprocess,'Popen',return_value=process) as launch, \
             patch.object(d.e.urllib.request,'urlopen',return_value=response), \
             patch.object(Path,'read_text',return_value='{}'):
            model=d.e.Qwen(Path(folder))
            try:
                command=launch.call_args.args[0]
                self.assertEqual(command[command.index('--device')+1],'none')
                self.assertIn('--no-op-offload',command)
                self.assertIn('--no-kv-offload',command)
                self.assertEqual(command[command.index('--pooling')+1],'last')
                self.assertEqual(command[command.index('--threads')+1],'4')
                self.assertEqual(command[command.index('--threads-batch')+1],'4')
                self.assertEqual(command[command.index('--ctx-size')+1],'2048')
                self.assertEqual(command[command.index('--batch-size')+1],'1024')
                self.assertEqual(command[command.index('--ubatch-size')+1],'1024')
                self.assertEqual(Path(command[command.index('-m')+1]).name,'Qwen3-Embedding-0.6B-Q4_K_M.gguf')
            finally:model.close()
        process.terminate.assert_called_once()


if __name__=='__main__':unittest.main()
