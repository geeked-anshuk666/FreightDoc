# Deployment guide

FreightDoc is deployed as two independently releasable applications:

| Surface | Platform | Build output | Responsibility |
|---|---|---|---|
| FastAPI API | Render free web service | `backend/Dockerfile` | pipeline, rules, document intake, PDFs, owner-scoped data |
| React/Vite PWA | Vercel free plan | `frontend/dist` | public product surface, Clerk UI, authenticated workspace |
| Postgres | Neon free plan | managed service | shipment and extracted-document metadata once persistence is enabled |

The frontend uses Vercel's native Vite build rather than a frontend container.
The backend image is retained because it produces a reproducible Python runtime
on Render.

## Before deployment

1. Rotate any credential that has ever been pasted into a chat, terminal
   transcript, screenshot, or source file.
2. Verify that no `.env` file, database dump, original uploaded file, or
   private design/interview document is tracked. See
   [repository policy](repository_policy.md).
3. Run the same checks used in CI:

   ```powershell
   cd backend
   python -m pytest tests -q
   cd ..\frontend
   npm ci
   npm run build
   ```

4. Decide the exact public Vercel URLs before setting API CORS. Do not use a
   wildcard `ALLOWED_ORIGINS` value in a production environment.

## Render API deployment

`render.yaml` describes the service and contains **only variable names**. It
uses the `backend/` directory as the Docker build context and
`backend/Dockerfile` as the image recipe.

### Create the service

1. Push the repository to the Git provider connected to Render.
2. In Render, select **New +** → **Blueprint** and select the repository.
3. Confirm the `freightdoc-api` service uses the Free plan and `GET /health`
   as its health check.
4. Enter the following environment variables in the Render dashboard. Values
   belong in the dashboard, never in the Blueprint or source tree.

| Variable | Required | Purpose |
|---|---:|---|
| `GROQ_API_KEY` | Yes for AI pipeline calls | Server-side structured-output provider key |
| `ALLOWED_ORIGINS` | Yes | Comma-separated, exact Vercel production/preview origins allowed by CORS |
| `DATABASE_URL` | Required when owner-scoped persistence is enabled | Neon pooled Postgres connection URL |
| `MIGRATIONS_DATABASE_URL` | Required for controlled schema releases | Neon direct (non-pooled) Postgres URL; use only for Alembic |
| `CLERK_JWKS_URL` | Required when protected API routes are enabled | Clerk JWKS endpoint used to verify tokens |
| `CLERK_ISSUER` | Required when protected API routes are enabled | Expected Clerk token issuer |
| `CLERK_AUDIENCE` | Optional, instance-dependent | Expected token audience when configured in Clerk |
| `AI_PROVIDER` | No | Defaults to `groq`; retain an honest provider declaration |
| `AI_MODEL` | No | Defaults to the model configured by the codebase |
| `REQUEST_TIMEOUT_SECONDS` | No | Bound for outbound source/AI calls |
| `DOCUMENT_PARSER_TIMEOUT_SECONDS` | No | Bound for document extraction work |

The image runs as an unprivileged `freightdoc` user and honours Render's
injected `PORT`. Render may suspend an inactive free service; the first API
call after idle can therefore take noticeably longer than a warm request.

### Database migrations

Do **not** make an application process silently mutate production schema at
startup. Once the repository's Alembic migration files are present, run this
from a one-off Render shell/job or a controlled release step before enabling a
build that depends on a new schema:

```bash
cd backend
alembic upgrade head
```

Use the same repository revision and `MIGRATIONS_DATABASE_URL` as the release
job. Runtime application processes should continue to use pooled
`DATABASE_URL`. A failed migration is a release blocker: restore the previous application revision or
perform an intentional forward repair; do not delete Neon data to recover.

### Verify and roll back

After a deploy, verify:

```text
GET https://<render-service>/health  -> 200 {"status":"ok"}
OPTIONS /api/full-pipeline           -> only approved Vercel origin
POST protected route without token   -> 401 once Clerk protection is enabled
```

Use Render's **Manual Deploy → Deploy latest successful commit** to roll back
application code. Database migrations need their own reviewed downgrade or
forward-fix plan; an application rollback does not undo schema changes.

## Vercel PWA deployment

1. Import the repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Select Vite (or leave Vercel's automatic Vite detection enabled).
4. Use build command `npm run build` and output directory `dist`.
5. Configure the environment variables below for Production, Preview, and
   Development as appropriate.

| Variable | Required | Notes |
|---|---:|---|
| `VITE_API_URL` | Yes outside local development | Public Render API origin, without a trailing slash (the executable frontend reads this exact name) |
| `VITE_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key; client-visible by design but still configured per environment |

`frontend/vercel.json` preserves SPA deep links and adds browser security
headers. It deliberately sends `no-store` for the service-worker entry points
so deployed PWA updates are discovered. Hashed Vite assets retain Vercel's
normal immutable cache behaviour. Do not add authenticated API responses,
upload bytes, generated PDFs, or Clerk responses to Workbox runtime caches.

### Clerk and CORS checklist

- Add each Vercel production domain and any needed preview domain to Clerk's
  allowed origins/redirect URLs.
- Set `ALLOWED_ORIGINS` on Render to the exact Vercel origins, separated by
  commas. Include `http://localhost:5173` only for a local environment.
- Confirm frontend requests attach Clerk's session token only to the API
  origin; never embed a backend credential in a `VITE_` variable.

## Local smoke test

Run the services in separate shells:

```powershell
# API
cd backend
python run_local.py

# PWA
cd frontend
npm run dev
```

Then request `http://127.0.0.1:8000/health`, open the Vite URL, and confirm
the browser console has no blocked CORS request or service-worker error.

The Vercel build should expose `VITE_API_URL` and
`VITE_CLERK_PUBLISHABLE_KEY` in the same deployment environment. A similarly
named variable such as `VITE_API_BASE_URL` is ignored by the current client
and can silently send requests to the localhost fallback, so treat that name
as a configuration error.

## Free-tier operating limits

- Render free instances can cold-start and are not an SLA-backed production
  service. The UI must show a recoverable API timeout state.
- Neon free compute/storage and Vercel free bandwidth have quotas. Monitor the
  providers' dashboards before a demo and delete user-owned test shipments
  rather than retaining them indefinitely.
- A free Render service is not a safe place to host a resident antivirus
  daemon. FreightDoc's baseline is strict type/signature/resource sanitation;
  connect a managed malware scanner before accepting untrusted files at
  material scale.

See [troubleshooting](troubleshooting_guide.md) for common failures and
[known tradeoffs](known_tradeoffs.md) for intentional scope limits.
