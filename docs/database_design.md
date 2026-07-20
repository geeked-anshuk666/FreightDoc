# Database design

Neon Postgres stores owner-scoped FreightDoc workspace data through async SQLAlchemy and Alembic. The initial migration is `backend/alembic/versions/20260720_0001_owner_scoped_workspace.py`.

| Table | Purpose | Boundary |
|---|---|---|
| `shipments` | Draft/review state and entered shipment facts | Opaque Clerk `owner_id`; no Clerk profile data. |
| `trade_parties` | Exporter/importer directory | User-entered commercial data only. |
| `intake_documents` | Extraction metadata, text, findings, confidence | Never stores original upload bytes. |
| `generated_packages` | Classification, provenance, generated documents, validation, inline MVP PDFs | Deleted with its shipment. |
| `validation_findings` | Structured critical/warning findings | Linked to generated package. |
| `audit_events` | Minimal action/request-ID history | No payload copies, tokens, or document content. |

Foreign keys cascade from shipments to documents/packages and from packages to validation findings. Repository methods always filter by the verified user’s `owner_id`. Small free-tier indexes include `(owner_id, created_at)`, `(owner_id, status)`, and owning shipment/package foreign keys.

Deleting a shipment deletes its associated document records, generated packages, findings, and PDFs. The account export/delete endpoints give users review and deletion control. Connections use a deliberately small Neon-compatible pool; see [deployment](deployment_guide.md).
