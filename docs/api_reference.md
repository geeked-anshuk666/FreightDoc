# API reference

All endpoints are served beneath `/api` except `GET /health`. API outputs are informational preparation data, not legal filing advice. Every response carries an `X-Request-ID` header for support and audit correlation.

## Public endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check for Render and local development. |
| `GET` | `/api/country-pairs` | Supported corridors and the China-to-specific-EU-member rule. |
| `POST` | `/api/full-pipeline` | Runs classification, deterministic tariff/rule stages, document generation, validation, and PDF rendering for a `ShipmentRequest`. |
| `POST` | `/api/classify`, `/api/generate`, `/api/validate` | Individually testable structured pipeline stages. |

`ShipmentRequest` requires `product_name`, `product_description`, ISO origin/destination country codes, positive `quantity`, positive `declared_value`, a three-letter `currency`, and optional exporter/importer names. The supported corridors are US→DE/GB/IN/JP/CA/AU, IN→US, and CN→a specific EU member.

## Authenticated workspace endpoints

These routes require a valid Clerk bearer token. The server verifies the JWT and scopes every record to its opaque `sub` claim; a client cannot provide an owner ID.

| Method | Path | Purpose |
|---|---|---|
| `POST`, `GET` | `/api/shipments` | Create a draft or list the current user’s shipments. |
| `GET`, `PATCH`, `DELETE` | `/api/shipments/{id}` | Read, update, or permanently delete an owner-scoped shipment. |
| `POST` | `/api/shipments/{id}/review` | Validate a draft and mark it ready for review. |
| `POST`, `GET` | `/api/parties` | Create or search the caller’s exporter/importer directory. |
| `POST`, `GET` | `/api/shipments/{id}/documents` | Submit/list typed intake documents; originals are never retained. |
| `DELETE` | `/api/shipments/{id}/documents/{documentId}` | Remove extracted document metadata/text. |
| `POST` | `/api/shipments/{id}/documents/{documentId}/retry` | Rerun supported extraction. |
| `POST` | `/api/shipments/{id}/dossiers` | Run and persist a reviewable dossier. |
| `GET` | `/api/shipments/{id}/dossiers/latest` | Return the latest owner-scoped dossier. |
| `GET` | `/api/shipments/{id}/dossiers/{packageId}` | Return a selected dossier. |
| `GET` | `/api/shipments/{id}/dossiers/{packageId}/download/complete.pdf` | Owner-checked complete dossier PDF stream. |
| `GET` | `/api/shipments/{id}/dossiers/{packageId}/download/{document}.pdf` | Owner-checked individual PDF stream. |
| `GET`, `DELETE` | `/api/account/export`, `/api/account/data` | Export or delete the caller’s stored FreightDoc data. |

## Intake policy and errors

The upload boundary accepts PDF, DOCX, XLSX, CSV, PNG, and JPEG only: **15 MiB per file**, **40 MiB aggregate**, **10 files per request**. Extension, declared MIME type, and content signature must agree. Office archives, PDFs, images, and CSV files receive resource limits before native parsing. Stable error codes include `FILE_TOO_LARGE`, `TYPE_MISMATCH`, `UNSAFE_ARCHIVE`, `CONTENT_LIMIT_EXCEEDED`, `ENCRYPTED_FILE`, `OCR_UNAVAILABLE`, and `EXTRACTION_FAILED`.

See [low-level design](lld.md) for schemas and [security architecture](security_architecture.md) for retention and ownership rules.
