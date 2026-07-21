# API reference

FastAPI serves `GET /health`, `/docs`, public `/api` routes, and authenticated owner-scoped workspace routes. Responses are informational preparation data, not legal filing advice. `X-Request-ID` is returned for support correlation.

## Public `/api` routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/country-pairs` | Supported corridors and China-to-specific-EU-member rule. |
| POST | `/api/classify`, `/api/generate`, `/api/validate`, `/api/full-pipeline` | Individually callable or combined draft pipeline stages. |

`ShipmentRequest` includes product name/description, ISO origin and destination, positive quantity/value, three-letter currency, and optional party names. `GET /health` is outside `/api`.

## Authenticated `/api` workspace routes

`/shipments`, `/parties`, document intake, dossier, and account-export/delete routes require Clerk verification when enabled and scope records to the server-derived owner. Dossier/download and document actions are ownership-checked. Intake accepts PDF, DOCX, XLSX, CSV, PNG, and JPEG with bounded resource checks; originals are not retained.

## Authenticated `/api/v1` record and operations routes

Canonical record endpoints cover shipment records, facts, revisions, review tasks/decisions, quality, suggestions, and audit history. Additional local surfaces cover rules/playbooks, candidate/ruling lookup, landed-cost scenarios, operations health/metrics/runs, connector mock runs, partner grants, screening/clearance cases, governance, and implementation resources.

These are reviewable/manual or mock/local surfaces where labelled. They do not file, clear, certify, screen, or perform a live external action without an approved integration. Use `/docs` at the running API for request/response schemas.
