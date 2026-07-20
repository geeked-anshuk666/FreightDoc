# Low-level design

## Pipeline contract

`ShipmentRequest` is the six-stage boundary. It forbids unknown fields, trims input, rejects unsupported control characters, bounds text/value/quantity, normalizes country/currency codes, and enforces supported corridors. The frontend labels location/category/shipping-method fields as preparation context when they are not part of this request contract.

Pipeline outputs are independently typed as `ClassificationResult`, `TariffData`, `DocumentRequirements`, `DocumentPackage`, `ValidationResult`, and `PdfArtifact`. Structured AI output is Pydantic-validated before use. Malformed output gets one provider retry before a safe error response.

## Services

| Module | Responsibility |
|---|---|
| `services/groq_client.py` | Configured structured classification, generation, and validation calls. |
| `services/hts_api.py`, `tariff_api.py` | Bounded source lookups with provenance and fallback semantics. |
| `services/doc_engine.py` | Versioned deterministic country/category document rules. |
| `services/pipeline.py` | Tariff orchestration, deterministic consistency checks, PDF orchestration. |
| `services/upload_policy.py` | Signature/resource limits before parsing untrusted uploads. |
| `services/document_intake.py` | Native bounded extraction and reviewed fact suggestions. |
| `repositories/freight_repository.py` | Owner-scoped persistence and minimal audit events. |

## Auth and persistence

`auth.py` validates Clerk JWTs and exposes only `CurrentUser(owner_id)`. Route dependencies receive sessions from `database.py`; `FreightRepository` applies ownership to every resource lookup. Alembic controls schema lifecycle. See [API reference](api_reference.md) and [database design](database_design.md) for the exposed route/table contracts.
