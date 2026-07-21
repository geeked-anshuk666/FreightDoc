# FreightDoc

FreightDoc prepares a reviewable export-documentation dossier from shipment facts. It is preparation software—not a customs broker, legal adviser, screening authority, carrier, or filing/clearance service—and a human reviewer remains responsible for consequential decisions.

## What is built

- Deterministic country-rule and document-requirement workflow with provenance and fallback labels.
- Reviewable shipment facts, revisions, review tasks, quality findings, and audit history.
- Structured draft documents and PDF dossier exports.
- Bounded document intake: original upload bytes are processed transiently; only permitted metadata and reviewed facts may persist.
- Local rules/playbooks/rulings, landed-cost scenarios, operations views, and clearly labelled manual/mock connector surfaces.

## Workflow

1. Create a shipment and add facts or safe source documents.
2. Generate and validate a draft using deterministic rules first.
3. Review findings and accept, correct, or waive them with a recorded decision.
4. Export an internally review-ready dossier. Export is not filing or clearance.

## Supported corridors

US to Germany, UK, India, Japan, Canada, or Australia; India to US; and China to a specified EU member state. `EU` alone is rejected for the China route because a destination country is required. See [known tradeoffs](docs/known_tradeoffs.md).

## Architecture and AI boundaries

The frontend is React/Vite/PWA with Clerk; the API is FastAPI, SQLAlchemy, and ReportLab. Persistence uses Postgres/Neon when configured. Render and Vercel configuration is included for deployment.

The workflow remains usable without an AI key. Runtime suggestions are optional, configured separately (currently Groq-oriented), labelled when unavailable/fallback, and must be accepted by a person. See the [deterministic AI safety contract](docs/deterministic_ai_safety_contract.md).

## Local setup

Prerequisites: Python 3.11+ and a current Node/npm installation.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_local.py
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

The API health check is `http://127.0.0.1:8000/health`. Configure values locally; never commit them. Names are `GROQ_API_KEY`, `AI_PROVIDER`, `AI_MODEL`, `DATABASE_URL`, `MIGRATIONS_DATABASE_URL`, `ALLOWED_ORIGINS`, `CLERK_JWKS_URL`, `CLERK_ISSUER`, optional `CLERK_AUDIENCE`, `REQUEST_TIMEOUT_SECONDS`, and `DOCUMENT_PARSER_TIMEOUT_SECONDS`. The frontend uses `VITE_API_URL` and `VITE_CLERK_PUBLISHABLE_KEY`.

### Synthetic demo shipment

Use only synthetic data for a demo or local test:

```json
{
  "product_name": "Aurora wireless earbuds",
  "product_description": "Retail-packaged Bluetooth earbuds; synthetic demonstration product.",
  "origin_country": "US",
  "destination_country": "DE",
  "quantity": 500,
  "declared_value": 25000,
  "currency": "USD",
  "exporter_name": "Northstar Demo Goods LLC",
  "importer_name": "Rhein Demo Retail GmbH"
}
```

The US-to-Germany electronics path visibly exercises a conditional CE declaration requirement. Do not upload customer records or credentials.

## Tests and deployment

```powershell
cd backend
python -m pytest tests -q

cd ..\frontend
npm ci
npm run test
npm run build
```

Deploy the API with [Render configuration](render.yaml) and the frontend with Vercel (root directory `frontend`). See the [deployment guide](docs/deployment_guide.md); free tiers may cold-start.

## Documentation

Start at the [documentation index](docs/documentation_index.md). It links the [system overview](docs/system_overview.md), [API reference](docs/api_reference.md), [testing strategy](docs/testing_strategy.md), [repository policy](docs/repository_policy.md), and [release checklist](docs/release_checklist.md).

## Build Week disclosure

Development-tool use is distinct from runtime AI. The repository records only verified claims in the [AI usage disclosure](docs/ai_usage_disclosure.md). Before submission, complete its evidence checklist and place the Codex `/feedback` session ID in the submission form—not in a public transcript.
