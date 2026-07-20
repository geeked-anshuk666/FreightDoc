# Testing strategy

FreightDoc tests the facts that make an export dossier safe to review: route
eligibility, deterministic document requirements, provenance/fallback status,
structured-output validation, PDF bytes, upload rejection, and owner scope.
Tests must not require a live AI key, Clerk account, public tariff source, or
real trade document.

## Test layers

| Layer | Scope | Examples |
|---|---|---|
| Unit | pure validators/services | supported corridor resolution, China→EU-member rule, conditional CE document, PDF `%PDF` output, filename/type/resource limits |
| Service integration | mocked external boundaries | malformed AI response retries once, tariff timeout selects labelled fallback, source provenance persists, sanitizer cleanup runs on failure |
| API integration | FastAPI client + test database | correlation header, 401/403 owner boundaries, draft CRUD, document retry/delete, authorised download |
| Migration | ephemeral Neon-compatible Postgres | `upgrade head`, schema assertions, downgrade/forward migration safety |
| Frontend | component and browser tests | combobox keyboard navigation, document upload states, raw-JSON regression guard, error boundary, readiness layout, OAuth presentation |
| End-to-end | mocked provider/source environment | sign in → save draft → upload/sanitize → review extracted facts → pipeline → view findings → authorised PDF download → delete shipment |

## Security-critical upload fixtures

Maintain harmless fixture files for:

- wrong extension versus magic bytes/MIME;
- over-limit body and aggregate request;
- encrypted/over-page PDF;
- archive traversal, excessive member count, and compression-ratio abuse;
- image decompression/pixel-limit abuse;
- malformed CSV/XLSX/DOCX;
- parser timeout/failure and proof that temporary bytes are removed.

Never put a malware sample, customer document, real credential, or production
database export in the test repository.

## Required CI commands

GitHub Actions runs the following on pushes to `main` and pull requests:

```text
backend:  python -m pytest tests -q
frontend: npm ci && npm run build
policy:   reject tracked .env files and common high-risk token prefixes
```

Run the same commands locally before a deployment. Add format/lint/type checks
only after their configuration is committed; an unconfigured tool that fails
every new clone is not a meaningful quality gate.

## Release verification

Before promoting a Render/Vercel deployment, verify `/health`, exact CORS
origins, public/noindex separation, Clerk negative authorization, source
fallback labelling, file rejection codes, a successful renderable PDF, and
user-owned deletion. Record only correlation IDs and redacted outcomes in a
release note.
