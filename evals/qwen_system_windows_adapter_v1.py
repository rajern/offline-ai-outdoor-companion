"""Windows asyncio loopback compatibility, frozen before any Qwen inference."""
import socket
from pathlib import Path
import run_qwen_rag_system_v1 as q

STATE = q.RUN / 'revision-02'
DOC = q.ROOT / 'evals/qwen_rag_system_technical_adapter.v1.md'
ORIGINAL_CONNECT = socket.socket.connect
ORIGINAL_CONNECT_EX = socket.socket.connect_ex
ORIGINAL_CREATE = socket.create_connection
ORIGINAL_WRITE = q.write_once


def is_loopback(address):
    return isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1')


def offline():
    q.t.s.holdout_guard()
    def connect(sock, address):
        if not is_loopback(address):
            raise PermissionError('External network disabled in system test')
        return ORIGINAL_CONNECT(sock, address)
    def connect_ex(sock, address):
        if not is_loopback(address):
            raise PermissionError('External network disabled in system test')
        return ORIGINAL_CONNECT_EX(sock, address)
    def create(address, *args, **kwargs):
        if not is_loopback(address):
            raise PermissionError('External network disabled in system test')
        return ORIGINAL_CREATE(address, *args, **kwargs)
    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.create_connection = create


def write_once(path, value):
    if path == STATE / 'freeze.json':
        value['identities'].update({str(p): q.sha(p) for p in
                                    [Path(__file__).resolve(), DOC]})
        value['offline_evidence'] = ('External Python sockets denied; numeric loopback allowed '
                                    'for Windows asyncio self-pipe; explicit local GGUF; '
                                    'OS network not disconnected')
        value['technical_revision'] = 'Windows asyncio socketpair compatibility; no previous Qwen calls'
    return ORIGINAL_WRITE(path, value)


def install():
    q.RUN = STATE
    q.offline = offline
    q.write_once = write_once


if __name__ == '__main__':
    install()
    q.main()
