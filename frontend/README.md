# Outwise frontend

Expo + React Native + TypeScript frontend for the Outwise PC MVP. The web target is the current development target; the layout remains phone-first for later mobile reuse.

## Run locally

Requires Node.js 22.13 or newer and pnpm.

```powershell
pnpm install
pnpm web
```

Open the URL printed by Expo. The frontend currently renders a static placeholder chat and does not call a backend or AI model.

## Checks

```powershell
pnpm typecheck
pnpm build:web
```
