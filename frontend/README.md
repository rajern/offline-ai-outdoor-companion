# Outwise frontend

Expo + React Native + TypeScript frontend for the Outwise PC MVP. The web target is the current development target; the layout remains phone-first for later mobile reuse.

## Run locally

Requires Node.js 22.13 or newer and pnpm.

```powershell
pnpm install
pnpm web
```

Open the URL printed by Expo. Start the backend on `http://127.0.0.1:8000` before sending a message. To use a different local address, set `EXPO_PUBLIC_API_URL` before starting Expo:

```powershell
$env:EXPO_PUBLIC_API_URL = "http://127.0.0.1:8000"
pnpm web
```

## Checks

```powershell
pnpm typecheck
pnpm build:web
```
