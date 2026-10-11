# Pre-inference technical revision 02

The first system launcher stopped before any Qwen call: denying all Python
socket connections also denied the numeric loopback socketpair required by the
Windows asyncio event loop. This is a test-isolation implementation error, not
an answer-quality result or a model failure. Its freeze, startup resource record
and stop remain unchanged in the original system-test directory.

`qwen_system_windows_adapter_v1.py` permits only numeric loopback (127.0.0.1,
::1) for the internal event loop and still denies external Python connections.
The API uses an in-process ASGI transport, not an external server. Runtime
execution still uses an explicit local GGUF. OS-level network disconnection is
not claimed. Adapter and this explanation join the immutable input/cache
identity before any inference under `revision-02`. Existing prompt, model,
settings, contexts, scorer, resource limits and answer protocol are unchanged.
No failed or successful Qwen inference was repeated for this correction.

The old backend Python 3.11 executable is unavailable. The existing project
Python 3.12 optimization environment and an isolated ignored directory containing
the project's FastAPI/httpx/pytest dependencies run the system tests. There is no
production dependency or environment change. 68 existing backend tests and six
system guard/cache tests passed before the baseline.
