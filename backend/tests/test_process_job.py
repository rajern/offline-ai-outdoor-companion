"""An abruptly stopped backend must not leave its model process running."""
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.skipif(os.name != 'nt', reason='Windows process ownership')
def test_child_is_stopped_when_backend_process_exits(tmp_path):
    record = tmp_path/'child.pid'
    script = '''
import subprocess,sys,time
from pathlib import Path
from outwise.services.process_job import ProcessJob
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(120)'])
job=ProcessJob(child)
Path(sys.argv[1]).write_text(str(child.pid))
print('ready',flush=True)
time.sleep(120)
'''
    parent = subprocess.Popen([sys.executable, '-c', script, str(record)], stdout=subprocess.PIPE, text=True)
    handle = None
    try:
        assert parent.stdout.readline().strip() == 'ready'
        child = int(record.read_text())
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        # Hold the exact child's handle before killing the parent; never kill by a reused PID.
        handle = kernel.OpenProcess(0x00100001, False, child)
        assert handle
        parent.kill(); parent.wait(timeout=10)
        assert kernel.WaitForSingleObject(handle, 5000) == 0
    finally:
        if parent.poll() is None: parent.kill(); parent.wait()
        if handle:
            if kernel.WaitForSingleObject(handle, 0) != 0:
                kernel.TerminateProcess(handle, 1)
            kernel.CloseHandle(handle)
