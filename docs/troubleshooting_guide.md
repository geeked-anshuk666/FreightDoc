# Troubleshooting guide

Start every API investigation with the `X-Request-ID` response header. It ties
frontend reports to the FastAPI request log without copying a shipment payload
into a ticket or log search.

## Deployment and availability

| Symptom | Likely cause | Safe resolution |
|---|---|---|
| Render reports an unhealthy deploy | `/health` is not returning 200, the process is not listening on Render's `PORT`, or startup failed before Uvicorn began | Read the Render build/runtime logs, verify `GET /health`, and confirm the Docker image has no local-only dependency. Roll back to the last successful service revision if necessary. |
| First pipeline request is slow after inactivity | Render free service cold start | Keep the frontend state recoverable; show retry rather than treating the session as failed. Do not add an unauthorised third-party uptime pinger to bypass free-tier policy. |
| Vercel shows a 404 on a deep link | SPA rewrite not applied or Vercel Root Directory is wrong | Set root directory to `frontend`, retain `frontend/vercel.json`, and redeploy. |
| Browser blocks API request | `ALLOWED_ORIGINS` does not exactly match Vercel scheme/host/port | Set the exact origins as a comma-separated Render variable. Do not use `*` with authenticated traffic. |
| PWA keeps showing an old UI | cached service-worker entry or browser has a stale worker | Reload once, open Application → Service Workers, and update/unregister only during local diagnosis. Production `sw.js` and `registerSW.js` are intentionally sent with no-store. |

## Authentication and owner scope

| Symptom | Likely cause | Safe resolution |
|---|---|---|
| Sign-in UI loads but protected API returns 401 | browser did not attach the Clerk token, token is expired, or Clerk API verification variables are missing | Check the request's `Authorization: Bearer` header in browser DevTools without copying the token elsewhere; configure `CLERK_JWKS_URL` and `CLERK_ISSUER` on Render. |
| API returns 403 for a shipment/document ID | record belongs to another Clerk subject | Treat this as expected owner-scope enforcement. Do not expose an existence check or retry with a changed owner ID. |
| Clerk redirects back to an error | Vercel domain is missing in Clerk's allowed origin/redirect settings | Add the exact deployment domain in Clerk, then retry in a private window. |

## Pipeline and external sources

| Symptom | Likely cause | Safe resolution |
|---|---|---|
| Structured AI stage fails | provider key/model configuration, timeout, or schema-conforming retry exhausted | Inspect the correlation ID and provider status. Do not substitute unvalidated prose into the dossier. |
| Tariff source reports fallback | an upstream source timed out, rate-limited, or returned unusable data | Surface source, retrieval time, and fallback flag. Treat fallback as informational and obtain broker/tariff-line review before filing. |
| China export destination rejected as `EU` | an actual EU member state is required for the supported corridor rule | Select a concrete ISO country such as `DE`, `FR`, or `NL`; do not generalise it to `EU`. |
| Low classification confidence or critical validation finding | shipment description lacks specificity or generated details conflict | Improve the product description and values, then rerun. Human customs-broker review is required before filing. |

## Document intake

FreightDoc must reject unsafe uploads rather than attempt to recover from them.
Expect a stable code/message for cases such as a size limit, type/signature
mismatch, unsafe archive, encrypted PDF, image pixel limit, parser timeout, or
unavailable OCR/malware scanner.

1. Verify the file is one of PDF, DOCX, XLSX, CSV, PNG, or JPEG.
2. Remove password protection and macros; export a clean PDF or office file.
3. Split unusually large scans into smaller documents rather than reducing
   server-side limits.
4. Review extracted fields before applying them to a shipment. Extraction is a
   suggestion, not an authoritative overwrite.
5. If extraction fails, retry only after correcting the file; never send a
   confidential original through a third-party conversion site merely to make
   it parse.

Original upload bytes are request-scoped and should be discarded after
sanitation/extraction. If a local temporary file remains after a failure,
treat it as a defect and remove it through the application's controlled
cleanup path rather than manually exposing it.

## Database and migrations

- `DATABASE_URL` must be a Neon Postgres URL usable by the API's async driver.
  Do not log the URL to test connectivity.
- Run an explicit Alembic migration step before deploying code that depends on
  a new schema. Avoid `create_all()` as a production repair mechanism.
- Connection exhaustion usually indicates too much free-tier concurrency or an
  unclosed session. Reduce API worker/concurrency settings and verify session
  cleanup/pool configuration before raising pool limits.

## Evidence to collect for a bug report

Provide the UTC time, route (without personal party/address data), API
correlation ID, HTTP status, redacted error code, browser version, and cold-start status. Do not attach raw trade documents, auth tokens, database URLs, or full AI prompts to public issues.
