# FreightDoc

FreightDoc prepares a reviewable export-documentation dossier from a shipment brief.

It classifies a product, retrieves tariff evidence, resolves country-specific document requirements, generates structured documents, cross-validates the package, and renders PDFs.

It is an **informational preparation tool**. FreightDoc is not a customs broker, broker-of-record, legal filing service, or guarantee of customs clearance. Low-confidence classifications, fallback tariff evidence, and critical validation findings require human customs-broker review.

## Product surfaces

| Component | Stack | Responsibility |
|---|---|---|
| `frontend/` | React, Vite, PWA, Clerk | public product experience and authenticated shipment workspace |
| `backend/` | FastAPI, Pydantic, ReportLab | pipeline orchestration, rule engine, source provenance, document/PDF processing |
| `backend/app/data/country_rules.json` | version-controlled JSON | deterministic document requirements and corridor conditions |
| `docs/` | Markdown | code-accurate operating, deployment, testing, and product boundaries |

The active provider/model is configuration-driven. The current executable backend configuration defaults to Groq; legacy planning documents that name a different runtime model are historical requirements, not a claim about the running service. See [known tradeoffs](docs/known_tradeoffs.md) before making product or compliance claims.

## Supported trade corridors

US→Germany, US→UK, US→India, US→Japan, US→Canada, US→Australia, India→US, and China→a specified EU member state. `EU` alone is intentionally rejected for a China export route because rules and tariff evidence need a real destination country.

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_local.py
```

The public health endpoint is `http://127.0.0.1:8000/health`.

### Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Set only variable **names** in local environment files. Required values depend on the features exercised:

| Backend | Frontend |
|---|---|
| `GROQ_API_KEY` | `VITE_API_URL` |
| `ALLOWED_ORIGINS` | `VITE_CLERK_PUBLISHABLE_KEY` |
| `DATABASE_URL` when persistence is enabled | |
| `CLERK_JWKS_URL`, `CLERK_ISSUER`, and optional `CLERK_AUDIENCE` when protected API routes are enabled | |

Never commit environment files, tokens, database URLs, or original uploaded documents. If a secret was shared outside an approved secret store, rotate it.

## Deployment

- **Backend:** Render Free, using [render.yaml](render.yaml) and [backend/Dockerfile](backend/Dockerfile).
- **Frontend:** Vercel Free with `frontend` configured as its root directory.
- **Database:** Neon Postgres through an environment-injected `DATABASE_URL`.

Use the [deployment guide](docs/deployment_guide.md) for dashboard settings, CORS/Clerk configuration, migration discipline, health checks, and rollback steps.

## Privacy and document handling

The owner-scope policy is deliberately narrow: protected routes verify Clerk JWTs and use only the opaque Clerk subject as `owner_id`. FreightDoc does not persist Clerk email, name, avatar, OAuth data, or session tokens by default.

Uploaded trade-document bytes are processed in a bounded temporary scope and must not be placed in logs, a PWA cache, or Postgres. Persist only the metadata and reviewed extraction facts that the product policy explicitly permits. See [troubleshooting](docs/troubleshooting_guide.md) and [known tradeoffs](docs/known_tradeoffs.md).

## Quality checks

```powershell
cd backend
python -m pytest tests -q

cd ..\frontend
npm ci
npm run build
```

The GitHub Actions workflow runs the same backend tests, frontend build, and a small tracked-file secret hygiene check. More test depth and release checks are listed in [testing strategy](docs/testing_strategy.md).

## Documentation map

- [System overview](docs/system_overview.md)
- [API reference](docs/api_reference.md)
- [Deployment guide](docs/deployment_guide.md)
- [Repository policy](docs/repository_policy.md)
- [Testing strategy](docs/testing_strategy.md)
- [Security architecture](docs/security_architecture.md)
- [Scaling path](docs/scaling_to_1_billion_users.md)
- [Known tradeoffs](docs/known_tradeoffs.md)
- [What we skipped and why](docs/what_we_skipped_and_why.md)
