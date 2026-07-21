# FreightDoc all-encompassing test-suite plan

## Purpose and guardrails

Build a deterministic, zero-cost test suite for the FastAPI backend and React/Vite PWA. The default lane must run without Clerk, Neon, Groq, tariff APIs, OCR workers, or network access; every external dependency is replaced with a fixture/fake. A separately documented live-smoke lane is opt-in and skipped when credentials are absent. Existing behavior and the current `backend/tests/test_pipeline_errors.py` and `backend/tests/test_backend_hardening.py` regressions remain intact.

No production application code is changed as part of this plan. Test-only dependencies and CI metadata may be added in the implementation phase.

## Test lanes and ownership

| Lane | Scope | Trigger | External services |
| --- | --- | --- | --- |
| Fast unit | Pure models, workflow/rules, upload policy/parsers, pipeline error mapping, PDF bytes | Every commit/PR | None |
| Backend contract/integration | FastAPI `TestClient`/`httpx`, dependency overrides, SQLite async repository, auth/owner isolation, multipart and downloads | Every PR | Fakes only |
| Frontend unit/component | Vitest + Testing Library; hooks, forms, dossier/download/error/auth/PWA components | Every PR | Mock `fetch`, Clerk, `URL`, `JSZip`, GSAP |
| Browser/accessibility | Playwright Chromium smoke at mobile/desktop, axe checks, keyboard and reduced-motion assertions | PR (or nightly if runtime is high) | Local Vite preview + fake API |
| Build/security/hygiene | Vite build/PWA artifact checks, secret scan, dependency audit, Docker import/startup | Every PR | None/network-free where possible |
| Live smoke (optional) | Health, country pairs, one classify/full-pipeline and authenticated shipment/download journey | Manual/nightly only, `FREIGHTDOC_LIVE_SMOKE=1` | Real Clerk/Groq/Neon/tariff endpoints; never required for merge |

## Files to create or update

### Backend

* `backend/pytest.ini` (markers `unit`, `integration`, `contract`, `live`, strict asyncio mode, coverage defaults).
* `backend/tests/conftest.py`: app fixture with dependency overrides, deterministic request ID, fake Clerk claims (`sub`, `org_id`), async SQLite engine/session, repository factory, seeded owner A/B records, fake Groq/tariff clients, temporary upload files, and teardown that disposes engines.
* `backend/tests/fixtures/`: minimal valid/invalid PDF, DOCX, XLSX, CSV, PNG/JPEG, encrypted PDF, malformed Office zip, zip-bomb metadata, formula CSV, and representative shipment/generation/validation JSON payloads. Keep fixtures synthetic and small.
* `backend/tests/test_models_and_rules.py`: Pydantic bounds, required fields, country corridor/rule lookup, status transition matrix, pagination cursor validation.
* `backend/tests/test_upload_policy_and_intake.py`: filename normalization/path traversal, MIME/signature mismatch, size/archive/page/cell/image limits, formula neutralization, extraction provenance, OCR-unavailable status, no-retention guarantees, parser timeout mapping.
* `backend/tests/test_pipeline_services.py`: classify→requirements→tariff→generation→validation→PDF orchestration, stage tagging, retries/timeouts, malformed/empty AI output, fallback tariff behavior, no provider text leakage, request correlation.
* `backend/tests/test_api_contract.py`: OpenAPI/status/schema assertions for `/health`, `/api/country-pairs`, `/classify`, `/generate`, `/validate`, `/full-pipeline`, including rate-limit and size-limit envelopes and security headers.
* `backend/tests/test_workspace_api.py`: authenticated CRUD and review/status transitions for shipments, parties, documents, dossier latest/list/detail, PDF downloads, account export/delete. Assert 401/403/404/409/422/413 behavior and idempotent deletes.
* `backend/tests/test_owner_scoping.py`: every shipment/document/party/dossier/account query is scoped to owner; foreign IDs return indistinguishable 404; cross-owner update/delete/download/apply/retry cannot mutate or disclose data.
* `backend/tests/test_auth_and_middleware.py`: Clerk JWT verification success/failure/expired/audience/issuer cases, missing config behavior, request-ID sanitization, body-size limits, CORS, CSP and other headers, rate limiter key caps.
* `backend/tests/test_pdf_generator.py`: generated PDF is non-empty, starts with `%PDF`, contains expected document sections/metadata, deterministic for fixed input, and fails safely on missing/invalid package data.
* `backend/tests/test_live_smoke.py`: all tests marked `live`, skip unless explicit flag and complete environment; use a disposable owner/shipment and clean up. Never assert exact provider wording.
* `backend/requirements-test.txt` (or additions to requirements): `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `aiosqlite`, `hypothesis` (optional), with pinned compatible versions.

### Frontend

* `frontend/vitest.config.js`, `frontend/src/test/setup.js`, and `frontend/package.json` scripts (`test`, `test:watch`, `test:coverage`, `test:e2e`, `lint` if introduced).
* `frontend/src/test/fixtures.js`: shipment/review/dossier/API error fixtures and deterministic Clerk/fetch responses.
* `frontend/src/components/*.test.jsx`: `AppErrorBoundary`, auth controls/experience, navigation, `ShipmentDesk`/`ShipmentForm`, dashboard, document tabs, dossier view, download bar, pipeline progress, warning/error panels, public-information, PWA status, and FullscreenCargoStory (GSAP mocked).
* `frontend/src/hooks/*.test.js`: `useFreightPipeline` and `useShipmentDashboard` success, loading, abort, retryable/non-retryable errors, stale-response and offline behavior.
* `frontend/e2e/*.spec.js`: desktop and 390px mobile journeys with mocked API/Clerk; review upload, suggestion application, status transition, dossier download/ZIP, sign-in/out redirects, offline shell and reduced-motion.
* `frontend/tests/accessibility.spec.js`: axe scan plus keyboard focus/order, labels, live regions, contrast-sensitive states, skip navigation, and no animation when `prefers-reduced-motion` is set.

### Repository/CI

* Extend `.github/workflows/ci.yml` with backend coverage, frontend unit/component, Playwright/a11y (sharded or optional), PWA artifact, secret scan and Docker smoke jobs. Preserve zero paid services.
* Add `docs/testing.md` with lane matrix, fixture policy, local commands, environment variables, live-smoke safety and triage guidance.
* Add `scripts/test.ps1` (Windows) and `scripts/test.sh` (CI/Linux) wrappers that run fast lanes consistently.

## Backend coverage matrix

1. **Models and domain rules** – valid/invalid `ShipmentRequest`, `GenerateRequest`, `ValidateRequest`, document/status enums; country-pairs including CN→EU and unknown corridor fallback; every legal/illegal `ShipmentStatus` transition.
2. **AI/pipeline** – fake Groq responses for valid JSON, schema-invalid JSON, provider 429/5xx, timeout, missing key, and retry exhaustion. Verify stable error codes, stage, request ID, retryability, `Retry-After`, and sanitized messages. Assert tariff API success, timeout/error, bounded fallback and source metadata.
3. **HTTP contract** – response models and content types for all routes (including PDF `application/pdf`, account export JSON, 204 deletes), query limits/cursors, malformed JSON, oversized bodies, rate limits, and correlation/security headers.
4. **Auth/ownership** – valid Clerk token, missing/bad token, unconfigured verifier, owner A/B fixtures, foreign resource indistinguishable 404, and account export/delete limited to current owner. Test repository queries always include owner predicate.
5. **Upload/parser/OCR policy** – six supported formats, extension/MIME/magic agreement, Unicode/path/device filename sanitization, empty/oversized files, malformed/encrypted PDFs, unsafe Office archives, CSV encoding/formula injection, workbook/page/image ceilings, text cap, parser timeout, OCR-unavailable status, and proof original bytes are not persisted/returned.
6. **Persistence/workflow** – create/list pagination/update/archive/delete shipment, party CRUD, document list/upload/apply/retry/delete, review notes/blockers/warnings, dossier run/list/latest/detail/download, audit events and transaction rollback on failures using SQLite.
7. **PDF** – deterministic ReportLab output, all document sections, filename/content-disposition sanitization, complete and individual downloads, and safe 404 for foreign package.
8. **Middleware/security** – request-ID CRLF/length rejection, 1 MiB JSON and 40 MiB multipart limits, CORS allowlist, CSP/frame/nosniff/referrer/permissions headers, rate limiter memory cap, and no secret/provider text in logs or envelopes.

## Frontend coverage matrix

* Render routes for signed-out, signed-in, loading, empty, error, offline and archived shipment states; assert Clerk redirects and sign-out behavior.
* `ShipmentForm` validates required fields, numeric bounds, corridor guidance and accessible errors; upload picker shows accepted types/size failures and extraction/OCR statuses.
* `ShipmentDesk` and dashboard exercise create/edit/list/review/status transitions, retry and stale request cancellation; verify API payloads and optimistic/rollback behavior.
* Dossier/document components render classification, requirements, tariff, generated docs, validation findings and confidence/provenance; critical blockers prevent review-ready action.
* Download bar requests PDF/ZIP, handles object URLs and cleanup, reports failures, and never trusts server filenames unsafely.
* Pipeline progress/error panels map backend stage envelopes, retry hints and request IDs to actionable text without leaking raw provider details.
* Fullscreen cargo hero mocks GSAP/Three where needed, remains usable without WebGL, and honors reduced-motion; assert no console errors.
* PWA status/offline shell checks manifest link, service worker registration, offline fallback, update prompt, cache denylist (API/auth routes not cached), and installability metadata.
* Accessibility/mobile checks cover semantic headings, labels, focus trap/order, keyboard-only operation, `aria-live`, touch targets, 390px overflow, and `prefers-reduced-motion`.

## Deterministic fixtures and mocking rules

* Set `FREIGHTDOC_ENV=test`, fixed UTC clock/request IDs where practical, and `DATABASE_URL=sqlite+aiosqlite:///:memory:` (or per-test temporary file for cross-connection tests).
* Override `require_current_user`, `get_db`, `GroqClient`, `TariffClient/HTSClient`, `render_complete_dossier`, and network calls; never import real SDK clients in fast tests.
* Use factory builders for two owners, one complete and one incomplete shipment, documents in `extracted`/`needs_ocr`/`failed` states, and dossier validation with critical/warning/ready cases.
* Use `respx`/`httpx.MockTransport` for outbound HTTP and `responses`/`vi.mock` for frontend fetch; assert call count, timeout and retry behavior.
* Live tests require explicit `FREIGHTDOC_LIVE_SMOKE=1`, `CLERK_*`, `GROQ_API_KEY`, database and tariff settings; mark destructive operations with a disposable prefix and cleanup fixture.

## Commands and quality gates

From PowerShell:

```powershell
cd backend
python -m pip install -r requirements.txt -r requirements-test.txt
python -m pytest tests -m "not live" --cov=app --cov-branch --cov-report=term-missing --cov-report=xml
python -m pytest tests -m live -q   # only with FREIGHTDOC_LIVE_SMOKE=1 and credentials

cd ..\frontend
npm ci
npm test -- --run
npm run test:coverage
npm run build
npx playwright install chromium
npm run test:e2e
```

CI should fail on backend <85% line / <75% branch coverage, frontend <80% statement / <70% branch coverage, contract failures, axe violations, missing PWA artifacts, tracked `.env` files or high-risk token patterns, and Docker startup failures. Keep thresholds ratchetable upward; do not lower them to accommodate flaky tests.

## Docker, CI and security checks

* Build backend image with `docker build --no-cache -t freightdoc-test backend` and run a health check with test settings; assert startup without external credentials and graceful `/health` response.
* Run `pip-audit`/`npm audit --omit=dev` in an informational or pinned-baseline job, plus repository secret scan matching the existing workflow patterns (`gsk_`, `npg_`, `sk_live/test_`, private-key headers) and tracked environment-file rejection.
* Ensure tests do not write outside temporary directories, do not retain upload bytes, and do not call production URLs. CI network may be limited to package installation and Playwright browser cache.

## Known Windows pytest teardown risk

On Windows, async SQLite/ReportLab/PyMuPDF handles or `NamedTemporaryFile` can keep files open, causing `PermissionError` during pytest cleanup. Fixtures must explicitly close uploads, dispose SQLAlchemy engines, close PDF/image/document handles, and use `TemporaryDirectory`/`Path.unlink(missing_ok=True)` only after context exit. Prefer `pytest --basetemp .pytest_tmp` under the workspace, remove it in a finalizer, and if a locked file remains mark the test failed with its path rather than recursively deleting broad directories. Run a dedicated Windows CI/local command (`python -m pytest tests -q --maxfail=1`) to catch teardown leaks; never hide them with `--basetemp` deletion or process-kill workarounds.

## Rollout sequence

1. Land fixtures/conftest and unit tests while preserving the two existing regression files.
2. Add API contract, auth/owner, persistence and upload integration tests against SQLite/fakes.
3. Add PDF/download and middleware/security assertions, then enforce backend coverage.
4. Add Vitest component/hook tests and frontend coverage; keep GSAP/WebGL/Clerk fully mocked.
5. Add Playwright/a11y/PWA and Docker/secret-scan jobs; quarantine only genuinely environment-dependent tests with explicit markers.
6. Document and manually run the live-smoke lane before releases; attach request IDs and redact credentials in reports.

## Definition of done

All listed routes and user journeys have deterministic tests; owner isolation and upload safety are proven; AI/tariff/Clerk/Neon integrations are mocked in required lanes; PDFs/downloads and PWA artifacts are validated; accessibility/mobile/reduced-motion checks pass; CI enforces coverage/security/build gates; Windows teardown is clean; and a repeatable, opt-in live-smoke procedure is documented without any paid service requirement.

## Verification status

Implemented deterministic coverage currently includes 41 backend tests and 19
frontend Vitest tests, plus cross-platform wrappers, tracked-secret hygiene
(with `.env.example` explicitly allowed), deterministic PWA artifact and
service-worker denylist checks, Docker/Render/Vercel descriptor validation, and
API route documentation checks. Playwright/axe browser tests, provider-backed
live smoke, and enforced coverage thresholds remain explicitly separate opt-in
lanes because they require additional browser tooling or credentials; they are
not silently represented as passing in the default zero-cost suite.
