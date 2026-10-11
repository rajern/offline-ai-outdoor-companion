import subprocess
import sys
import unittest
from pathlib import Path

import qwen_system_windows_adapter_v1 as adapter


class WindowsIsolationTest(unittest.TestCase):
    def test_only_numeric_loopback_is_permitted(self):
        self.assertTrue(adapter.is_loopback(('127.0.0.1', 12345)))
        self.assertTrue(adapter.is_loopback(('::1', 12345)))
        self.assertFalse(adapter.is_loopback(('example.com', 443)))
        self.assertFalse(adapter.is_loopback(('192.168.1.2', 12345)))

    def test_actual_asyncio_self_pipe_and_external_denial(self):
        code = (
            "import sys,asyncio,socket;sys.path.insert(0,'evals');"
            "import qwen_system_windows_adapter_v1 as a;a.offline();"
            "asyncio.run(asyncio.sleep(0));"
            "\ntry: socket.create_connection(('example.com',443))"
            "\nexcept PermissionError: print('external denied; local asyncio works')"
            "\nelse: raise AssertionError('external network allowed')"
        )
        result = subprocess.run([sys.executable, '-c', code],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('external denied', result.stdout)


if __name__ == '__main__':
    unittest.main()
