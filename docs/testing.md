# FreightDoc test and release checks

FreightDoc's default test lane is deterministic and zero-cost. It uses local
fixtures/fakes and does not require Clerk, Neon, Groq, tariff providers, OCR
workers, or production URLs. Live smoke tests are opt-in and never a merge
requirement.

## Local commands

From PowerShell:

```powershell
./scripts/test.ps1
```

To skip the npm install when dependencies are already present:

```powershell
./scripts/test.ps1 -SkipInstall
```

From Linux/macOS/CI:

```bash
./scripts/test.sh
```

The wrapper runs backend tests excluding `live`, frontend unit tests, builds the
Vite PWA, and executes `scripts/verify_release.py`. The release checker is
standard-library only and can be run independently.

## CI lanes

`.github/workflows/ci.yml` runs backend tests, the frontend build/PWA artifact
check, and repository hygiene on every push and pull request. The hygiene
check rejects tracked runtime `.env` files and high-risk token patterns while
allowing the tracked `backend/.env.example` template. The release checker also
validates the PWA manifest/service worker denylist, Docker/Render/Vercel
descriptors, and the documented API route contract.

The default component lane is active: `npm test -- --run` currently covers 7
files and 19 tests. Playwright/axe browser coverage and numeric coverage gates
remain opt-in until their tooling is deliberately added; they must continue to
use local mocks and should not introduce paid services or credentials into CI.

## PWA and deployment checks

The production build must contain `index.html`, `manifest.webmanifest`,
`sw.js`, and `offline.html`. The service worker must denylist `/api/`,
`/sign-in`, and `/sign-up` navigation so authenticated/API responses are not
cached. `render.yaml` remains on the Free plan with `/health` and dashboard-
managed secrets; `frontend/vercel.json` must preserve SPA fallback and security
headers. Docker startup is expected to honor Render's dynamic `PORT`, run as
the non-root `freightdoc` user, and expose a `/health` healthcheck.

## Optional live smoke

Live checks are deliberately separate from merge CI. Set
`FREIGHTDOC_LIVE_SMOKE=1` only in a disposable environment and provide the
required Clerk, Groq, database, and tariff settings. Use a disposable owner
and shipment prefix, redact request IDs/credentials from logs, and clean up
created records. Tests should assert health/status and schema shape rather than
provider wording. If credentials or the explicit flag are absent, the live
lane must skip instead of failing the default suite.

## Triage and safety

Run a failing lane directly to obtain focused output (`python -m pytest tests
-q --maxfail=1` in `backend`, or `npm run build` in `frontend`). Keep temporary
files under the workspace or the OS temporary directory and close async
database/PDF/parser handles before fixture teardown, especially on Windows.
Never commit `.env` files, provider keys, generated `dist` output, or uploads.
