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

Run the release commands from the exact candidate revision and record observed
counts rather than copying historical totals:

```powershell
cd backend
python -m pytest tests -q
cd ..\frontend
npm ci
npm run test
npm run build
```

## Foundation safety matrix (Phase 0/1)

Add route-level tests as each capability lands; do not add speculative tests
that bind CI to an unfinished route name. The default lane uses a disabled or
fake AI adapter and local fixtures only.

| Contract | High-value assertion |
|---|---|
| Tenant boundary | A second owner/organization receives the same 404 for another tenant's shipment, fact, review task, audit event, export, or download; it cannot mutate any of them. |
| Revisions and stale writes | A write with an old revision number is rejected with a conflict and does not create a partial fact/audit change. Human edits create an immutable revision. |
| Provenance | Every accepted extracted/AI-suggested fact has source/evidence identifiers, provenance, confidence where applicable, and the accepting/rejecting actor/action in audit history. |
| AI disabled/unavailable | A complete manual/native-extraction, quality, review, template, and export workflow succeeds with no AI configuration. Timeout/malformed/low-confidence output creates a visible manual-review state and makes no authoritative change. |
| Maker/checker | With separation enabled, the maker cannot approve their own task; an authorized different actor can decide with a reason. |
| Intake/dedupe/privacy | Re-uploading identical allowed bytes detects the SHA-256 duplicate without persisting originals. Logs, database records, PWA cache fixtures, and AI request fixtures contain no raw upload bytes. |
| Quality/export | Unresolved critical conflicts block export; resolution/waiver is attributable. ZIP manifest hashes match its included artifacts and records pinned rule/template/fact versions plus disclaimer. |
| Feature flags/rollback | New capabilities default off; disabling a flag restores the deterministic/manual path without deleting revisions, audit history, or prior manifests. |
| Disconnected authority adapters | Screening remains `not screened`; clearance remains `not connected`/`not filed`; mock/CSV connectors never report a live, cleared, filed, or certified state. |

Recommended focused commands after the related routes/models are merged:

```text
cd backend && python -m pytest tests -q
cd frontend && npm test -- --run && npm run build
python scripts/verify_release.py
```

## Phase 2–4 deterministic baseline matrix

The following contracts define the test gate for governed knowledge,
decision-support, and adapter scaffolding. Test public service contracts or
completed routes only; all fixtures must be local and must not call a tariff,
AI, sanctions, customs, carrier, identity-provider, or connector service.

| Area | Required deterministic test contract |
|---|---|
| Rules and playbooks | Evaluation from the same pinned rule/playbook version and facts is reproducible. A draft or invalid version cannot become published; an unauthorized owner/organization receives the ordinary not-found/forbidden boundary. Publishing a new version never changes an already pinned result. |
| HS candidates and rulings | Local search returns cited curated candidates without presenting them as official rulings. A manual selection records actor, rationale, source/version, and advisory status. AI ranking failure leaves candidate search and manual choice usable; it cannot choose or overwrite the decision. |
| Landed-cost scenarios | Explicit inputs produce traceable line items. Changing an assumption changes only the corresponding calculation/result revision. Missing, expired, or fallback tariff/FX/tax evidence produces `unknown` or a labelled range and a review finding—never a synthetic confirmed rate or total. |
| Connector gateway | Mock/local/CSV adapter runs log a bounded status and correlation identifier, while returned configuration never contains a secret. Disabled adapters visibly remain `mock`, `not configured`, or `requires approved vendor`; an error never becomes a successful external action. |
| Restricted-party screening | A new/manual case begins `not screened`. No local similarity result, AI output, absence of a provider, or error may set `cleared`. A final disposition requires an authorized human decision and an authoritative-source reference; test every alternative state against this invariant. |
| Clearance and filing | A manual case begins `not connected` and `not filed`. Evidence import may create a timeline entry, but no route/adapter/AI response may submit, file, accept, or clear a declaration without an activated authorized integration. |
| Governance and collaboration | Every organization-scoped rule, playbook, scenario, connector run, screening/clearance case, role/policy, grant, and audit read/write rejects a different owner/organization without enumeration. Expired/revoked grants cannot access artifacts or initiate actions. |
| No-AI path | Force all AI methods to raise a provider/configuration error and assert that deterministic rules, candidate search, scenario calculations, manual review, mock/manual adapter workflows, and dossier preparation remain usable. Assert fallback/manual-review labels and that no final/legal/regulated status changes. |

Add a regression test whenever a new status is introduced. Status tests should
assert both the permitted transition and every prohibited authority claim
(`cleared`, `filed`, `accepted`, `live`, `certified`) while the corresponding
adapter is disabled or mock.
