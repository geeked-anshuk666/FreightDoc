# Scaling FreightDoc responsibly

"One billion users" is a design exercise, not a claim about the current
free-tier deployment. The current Render + Vercel + Neon setup is appropriate
for a hackathon demo and early validation, not sustained global traffic or
legal filing operations.

## Scaling stages

| Stage | Architecture | Trigger to move on |
|---|---|---|
| Demo | one Render API, Vercel static/PWA delivery, Neon free database, synchronous pipeline | cold starts, quotas, or a handful of concurrent long-running pipelines impair the demo |
| Early customers | container platform with multiple API instances, managed Postgres, Redis, object storage only for explicitly retained artefacts | regular pipeline contention, database pool saturation, need for operational support |
| Regional product | queue-backed document extraction/generation, per-region workers, CDN public marketing surface, regional source-routing | latency/residency requirements or sustained cross-region traffic |
| Global platform | multi-region control plane, partitioned data, event stream, isolated customer tenants, disaster recovery and audited change control | verified product-market fit and a funded reliability/compliance program |

## Request path

Keep latency-sensitive work separate from resource-intensive work:

1. An API edge authenticates the Clerk token, applies rate/size limits, and
   assigns a correlation ID.
2. Owner-scoped metadata is stored transactionally in Postgres.
3. Document sanitation and OCR run in bounded workers with hard resource
   limits; original bytes are deleted unless a future retention policy says
   otherwise.
4. Classification, tariff retrieval, document generation, validation, and PDF
   rendering move through idempotent jobs when they exceed an interactive
   request budget.
5. The client polls or subscribes to a small status projection; it never
   reads queue payloads or raw source documents.

Every job needs an owner ID, correlation ID, idempotency key, bounded retry
policy, dead-letter path, and redacted audit event.

## Data and tenancy

- Use the opaque Clerk subject as the tenant boundary. Do not copy Clerk
  profile data unless a separate privacy decision requires it.
- Index all owner-scoped lookups, especially `(owner_id, created_at)` and
  foreign-key joins from shipment to document/dossier/finding.
- Move from a shared Postgres database to tenant-aware partitioning only when
  measured table size, residency, or noisy-neighbour behaviour justifies it.
- Back up schema and user-owned records; test restores. A tariff-rule JSON
  change is versioned configuration and needs an auditable deployment path.

## Caching without privacy leaks

HS classification can be cached only after normalising a description and
including inputs that change the result: origin, destination, rules version,
provider/model version, and prompt/schema version. Use a short TTL and
invalidate on model/rule/prompt changes. Do not use raw upload bytes as cache
keys and never allow a cache lookup to reveal another user's shipment.

Tariff/source responses require their own source timestamp, route/HTS key,
expiry, fallback flag, and provenance. Cached or fallback data must never be
displayed as live duty evidence.

## Reliability objectives

Measure rather than promise:

- API availability, p50/p95 pipeline duration, cold-start rate, and external
  source timeout/fallback rate.
- structured-output retry/failure rate by provider/model/schema version;
- document sanitation rejection code rate and bounded parser execution time;
- owner-scope denial rate, database connection usage, queue age, and PDF
  rendering failures.

At meaningful scale, publish an SLO and error budget, use distributed tracing
with correlation IDs, and create tested incident/rollback runbooks. Do not put
shipment descriptions, documents, bearer tokens, or database URLs in logs.

## Security and compliance gates before scale

Before expanding upload volumes or regions, add a managed malware scanning
service, independent security testing, encrypted backups, data-deletion export
workflows, vendor/data-processing reviews, shared rate limiting, and
broker/legal review of every market rule. Scaling infrastructure does not make
generated customs documentation legally sufficient.
