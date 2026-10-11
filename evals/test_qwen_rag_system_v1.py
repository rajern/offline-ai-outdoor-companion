"""Behavior checks for isolated inference preservation, cache and guards."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_qwen_rag_system_v1 as q


class ResourcesStub:
    def __init__(self, fail_after=999):
        self.checks = 0
        self.fail_after = fail_after
    def check(self):
        self.checks += 1
        if self.checks > self.fail_after:
            raise RuntimeError('Resource guard')
    def sample(self):
        pass
    def result(self):
        return {'guard': True}


class SystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_root = (q.ROOT / 'knowledge/local/judge-test-temp').resolve()
        assert cls.temp_root.is_relative_to(q.ROOT.resolve())
        cls.temp_root.mkdir(parents=True, exist_ok=True)

    def test_success_preserves_raw_output(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as name:
            directory = Path(name)
            assert directory.resolve().is_relative_to(self.temp_root)
            result = q.GuardedRunner(directory, ResourcesStub()).run(
                [sys.executable, '-c', "print('lokalt svar')"], 10)
            self.assertEqual(result.returncode, 0)
            self.assertIn('lokalt svar', (directory / 'stdout.txt').read_text())
            self.assertIsNone(q.read(directory / 'process.json')['error'])

    def test_guard_kills_and_retains_attempt(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as name:
            directory = Path(name)
            assert directory.resolve().is_relative_to(self.temp_root)
            with self.assertRaisesRegex(RuntimeError, 'Resource guard'):
                q.GuardedRunner(directory, ResourcesStub(fail_after=1)).run(
                    [sys.executable, '-c', 'import time;time.sleep(5)'], 10)
            self.assertTrue((directory / 'stdout.txt').exists())
            self.assertEqual(q.read(directory / 'process.json')['error'], 'Resource guard')

    def test_timeout_retains_attempt(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as name:
            directory = Path(name)
            assert directory.resolve().is_relative_to(self.temp_root)
            with self.assertRaises(subprocess.TimeoutExpired):
                q.GuardedRunner(directory, ResourcesStub()).run(
                    [sys.executable, '-c', 'import time;time.sleep(5)'], .1)
            self.assertTrue((directory / 'process.json').exists())

    def test_cache_binds_prompt_runtime_and_settings(self):
        frozen = {'settings': {'max_tokens': 256}, 'identities': {'runtime': 'a'},
                  'protocol_sha256': 'p'}
        key = q.cache_key(frozen, 'question/context')
        self.assertNotEqual(key, q.cache_key(frozen, 'other context'))
        frozen['settings']['max_tokens'] = 128
        self.assertNotEqual(key, q.cache_key(frozen, 'question/context'))
        frozen['settings']['max_tokens'] = 256
        frozen['identities']['runtime'] = 'b'
        self.assertNotEqual(key, q.cache_key(frozen, 'question/context'))

    def test_readonly_packing_tokens_never_compute_missing_input(self):
        with self.assertRaisesRegex(ValueError, 'No frozen tokenization'):
            q.ReadOnlyCounter().count('unique unrecorded system-test token input')

    def test_m3_history_and_checkpoints_unchanged(self):
        current = (q.ROOT / 'TASKS.md').read_text(encoding='utf-8')
        previous = subprocess.check_output(['git', 'show', '849a4ff:TASKS.md'],
                                           cwd=q.ROOT).decode('utf-8')
        marker = '# Milestone 3 — Safety + Finished MVP'
        self.assertEqual(current[current.index(marker):], previous[previous.index(marker):])


if __name__ == '__main__':
    unittest.main()
