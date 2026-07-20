# FreightDoc production release audit — 20 zero-cost improvements

Reviewed 2026-07-21 for the Render Free API and Vercel Free PWA. This is a
durable checklist for the tomorrow release pass. It intentionally contains
exactly twenty improvements; each row records implementation evidence and the
free-tier limitation that still needs honest operator attention.

| # | Zero-cost improvement | Status | Evidence | Free-tier caveat |
|---:|---|---|---|---|
| 1 | Keep the Render service explicitly on the Free plan with a health path. | Implemented | `render.yaml` (`plan: free`, `/health`) | Render may suspend an idle service; this is not an SLA. |
| 2 | Keep all production secrets out of the Blueprint and source tree. | Implemented | `render.yaml` marks secret values `sync: false`; `docs/deployment_guide.md` dashboard procedure | Render/Neon/Clerk quotas and rotation remain operator responsibilities. |
| 3 | Separate pooled runtime DB credentials from direct migration credentials. | Implemented | `render.yaml` declares `MIGRATIONS_DATABASE_URL`; `backend/.env.example`; deployment guide migration section | A free Neon database still has connection/storage limits. |
| 4 | Declare bounded outbound and parser timeouts in deployment config. | Implemented | `render.yaml` sets `REQUEST_TIMEOUT_SECONDS=8` and `DOCUMENT_PARSER_TIMEOUT_SECONDS=12` | Short timeouts do not prevent cold-start latency or provider rate limits. |
| 5 | Make the API image honor Render's injected `PORT`. | Implemented | `backend/Dockerfile` command and healthcheck use `PORT` | One free instance has limited CPU/RAM and can cold-start. |
| 6 | Use a multi-stage, non-root, slim Python image. | Implemented | `backend/Dockerfile` builder/runtime stages and `freightdoc` user | Image hardening does not provide host-level malware scanning. |
| 7 | Keep virtualenvs, tests, secrets, and local files out of Docker context. | Implemented | `backend/.dockerignore` | Build context is smaller, but dependency install still consumes build time. |
| 8 | Preserve a container healthcheck in addition to Render's health probe. | Implemented | `HEALTHCHECK` in `backend/Dockerfile` | Healthchecks restart unhealthy processes; they do not make the service highly available. |
| 9 | Document Vercel's native Vite root/build/output settings. | Implemented | `docs/deployment_guide.md` Vercel section | Vercel Free bandwidth/build quotas still apply. |
| 10 | Route SPA deep links to the Vite entry document. | Implemented | `frontend/vercel.json` rewrite to `/index.html` | API routes must remain on the Render origin; do not proxy private API data through Vercel. |
| 11 | Cache hashed Vite assets immutably. | Implemented | `frontend/vercel.json` `/assets/(.*)` cache header | A bad release requires a new hashed build; never reuse an asset filename. |
| 12 | Force fresh HTML and service-worker discovery. | Implemented | `frontend/vercel.json` no-store headers for `index.html`, `sw.js`, `registerSW.js`; revalidated manifest | Browsers may still hold an already-installed worker until it checks in. |
| 13 | Add baseline browser security headers at the Vercel edge. | Implemented | `frontend/vercel.json`: nosniff, frame denial, referrer, permissions policy | Headers do not replace Clerk/CORS/API authorization. |
| 14 | Keep PWA precache static-only and denylist API/auth navigations. | Implemented | `frontend/vite.config.js` empty runtime cache and navigation denylist | Offline mode is shell-only; authenticated data and uploads remain unavailable. |
| 15 | Provide an explicit offline/update status and safe offline page. | Implemented | `frontend/src/components/PwaStatus.jsx`, `frontend/public/offline.html` | No paid sync/storage is present; users must reconnect before processing shipments. |
| 16 | Verify PWA artifacts in CI after every production build. | Implemented | `.github/workflows/ci.yml` checks `dist/index.html`, manifest, worker, offline page, and denylist | CI catches missing artifacts, not browser-specific install quirks. |
| 17 | Make the deployed API variable name match executable frontend code. | Implemented | `docs/deployment_guide.md` uses `VITE_API_URL`; hooks read the same name | `VITE_API_BASE_URL` is ignored and falls back to localhost; treat it as an error. |
| 18 | Keep private/auth/API paths out of search crawling. | Implemented | `frontend/public/robots.txt` disallows `/api/`, `/sign-in`, `/sign-up` | Robots is advisory; authenticated routes still require application authorization. |
| 19 | Keep canonical/social metadata host-specific and environment-driven. | Implemented | `PageMetadata.jsx` reads `VITE_PUBLIC_SITE_URL`; `frontend/index.html` has accurate base metadata and Vite emits the manifest link | Do not publish a guessed sitemap or preview origin before the final domain exists. |
| 20 | Prevent local env/build artifacts and obvious tokens from entering Git. | Implemented | Root `.gitignore` covers `.env.*`, frontend env, `dist`, `node_modules`; CI hygiene job scans tracked files | Secret scanning is heuristic; rotate any credential ever exposed outside a secret store. |

## Verification record

- `frontend`: `npm.cmd run build` — passed (Vite 8.1.5; 14 PWA precache entries).
- `frontend`: artifact checks for `dist/index.html`, `manifest.webmanifest`,
  `sw.js`, `offline.html`, manifest link, and navigation denylist — passed.
- PowerShell `git check-ignore` confirms local frontend env/build paths are
  ignored; `git ls-files frontend/.env.local` returns no tracked file.
- Vulnerability scan: dependency, secret, and dangerous-pattern checks pass.
  Its remaining medium advisory is a detector limitation: it only recognizes
  Next/nginx header files, while FastAPI applies the same headers in
  `backend/app/main.py` middleware.
- Backend tests and a live Render/Vercel smoke test require the deployment
  environment and are intentionally not represented as local success here.

## Release stop conditions

Do not promote a build if `GET /health` is not `200`, CORS is broader than the
approved Vercel origins, a production secret appears in Git, the PWA worker
caches API/auth responses, or the deployed client still uses a localhost API
fallback. Free plans are suitable for a bounded demo, not an availability or
compliance guarantee.
