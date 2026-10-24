"""Behavioral checks for sealed input use and GGUF metadata; no model inference."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import resume_local_generation_v1 as r


class ResumeTests(unittest.TestCase):
    def test_native_chat_template_and_token_sequence_define_budget(self):
        item = {'id':'synthetic','messages':[{'role':'system','content':'instruction'},
                 {'role':'user','content':'source and question'}], 'context_sha256':'hash'}
        prompt = '<|im_start|>system\ninstruction<|im_end|>\n<|im_start|>user\nsource and question<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'
        def request(endpoint, data):
            return {'prompt':prompt} if endpoint == '/apply-template' else {'tokens':list(range(3200))}
        row = r.native_input(request, item, 4096, 262144, 'qwen-2b')
        self.assertEqual(row['input_tokens'],3200)
        self.assertEqual(row['tokens'][-1],3199)
        with self.assertRaisesRegex(RuntimeError,'context'):
            r.native_input(request,item,3500,262144,'qwen-2b')

    def test_training_context_comes_from_actual_gguf_and_arrays_are_skipped(self):
        parent = (r.p.ROOT / 'knowledge/local/judge-test-temp').resolve()
        parent.mkdir(parents=True,exist_ok=True)
        self.assertTrue(parent.is_relative_to(r.p.ROOT.resolve()))
        with tempfile.TemporaryDirectory(dir=parent) as folder:
            file = Path(folder) / 'synthetic.gguf'
            def string(s):
                b=s.encode();return struct.pack('<Q',len(b))+b
            file.write_bytes(b'GGUF'+struct.pack('<IQQ',3,0,3)+
                string('unused.array')+struct.pack('<IIQ',9,8,2)+string('ignored')+string('also ignored')+
                string('general.architecture')+struct.pack('<I',8)+string('synthetic')+
                string('synthetic.context_length')+struct.pack('<II',4,4096))
            self.assertEqual(r.gguf_metadata(file),{'general.architecture':'synthetic','synthetic.context_length':4096})

    def test_cache_seal_rejects_a_changed_result(self):
        with patch.object(r.q,'read',return_value={'answer.txt':'expected'}), patch.object(r.q,'sha',return_value='modified'):
            with self.assertRaises(AssertionError): r.verify_seal(Path('synthetic'))

    def test_only_rss_failure_with_intact_host_reserve_permits_exclusion(self):
        exclusion = {'qwen-4b': {'resource_path':'synthetic.json','resource_sha256':'match'}}
        observed = {'minimum_available_ram_bytes':r.RAM_RESERVE,'peak_process_tree_rss_bytes':r.RSS_LIMIT+1}
        with patch.object(Path,'exists',return_value=True), patch.object(r.q,'read',side_effect=[exclusion,observed]), patch.object(r.q,'sha',return_value='match'):
            self.assertEqual(r.eligible_models(),['qwen-2b','gemma-e2b'])
        observed['minimum_available_ram_bytes']=r.RAM_RESERVE-1
        with patch.object(Path,'exists',return_value=True), patch.object(r.q,'read',side_effect=[exclusion,observed]), patch.object(r.q,'sha',return_value='match'):
            with self.assertRaises(AssertionError): r.eligible_models()


if __name__ == '__main__': unittest.main()
