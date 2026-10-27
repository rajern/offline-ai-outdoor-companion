# Outwise frontend

Expo + React Native + TypeScript. The current target is a local web application
on PC; this is not a deployed native phone app. The screen displays exact source
excerpts before the automatically generated interpretation. Each question is
independent, even though the screen keeps a question/answer history.

## Run the complete application

From the repository root, after installing dependencies:

```powershell
.\scripts\start-outwise.ps1
```

Open `http://127.0.0.1:8000`. The script builds the frontend if necessary, then
FastAPI serves it with the API. Browser requests use the same origin; a custom
port passed to the script therefore works. No hosting service is needed.

The **Se demo** mode (`/?demo=1`) contains two real, saved Qwen screening outputs
and their source excerpts, clearly labeled as replay. No model or knowledge
setup is needed to view it. Source text uses the existing approved reuse terms
and visible attribution; see `demo/provenance.json` and
[scope and demo details](../docs/PROTOTYPE.md).

## Development

Requires Node 22.13+ and pnpm. From this directory:

```powershell
pnpm install --frozen-lockfile
$env:EXPO_PUBLIC_API_URL = 'http://127.0.0.1:8000'
pnpm web
```

Start FastAPI separately. The environment variable is needed when the Expo dev
server and API use different ports. It is not needed for the exported frontend
served by FastAPI. Rebuild with `pnpm build:web` after source changes if serving
an existing export.

## Checks

```powershell
pnpm typecheck
pnpm build:web
```

Missing backend/assets, waiting and generation errors are displayed explicitly.
The status badge reflects file availability, not proven offline readiness or
answer safety. External original/licence links need internet; the excerpts and
bundled replay are local. Final prototype copy and physical offline sign-off
remain subject to owner review.
