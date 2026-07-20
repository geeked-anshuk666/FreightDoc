# FreightDoc SaaS Product Roadmap

**Status:** product direction for post-hackathon delivery
**Owner:** solo founder
**Last updated:** 2026-07-20
**Planning principle:** make shipment preparation faster and more reviewable without presenting FreightDoc as legal advice or replacing a licensed customs broker.

## 1. Product thesis and positioning

FreightDoc should become the **shipment-documentation control plane for growing exporters**: one place to prepare an export shipment, collect source documents, produce a reviewable dossier, resolve exceptions, and preserve an audit trail.

The differentiator is not “AI writes documents.” It is a controlled workflow that combines:

- user-reviewed shipment facts;
- deterministic country/document rules and tariff evidence with provenance;
- structured AI assistance for classification, document drafting, and consistency checks;
- a clear exception queue before a shipment is released for broker review.

### Ideal customer profile

| Segment | Initial job-to-be-done | Why FreightDoc wins |
|---|---|---|
| Small and growing exporters | Prepare repeatable cross-border shipments without recreating paperwork | Guided workflow, templates, document intake, and visibility into missing information |
| DTC/e-commerce operations teams | Move frequent low-to-medium-complexity shipments with a small team | Shipment history, reusable parties/products, review queue, and predictable handoff |
| Freight forwarders and broker teams | Accelerate first-pass collection and review of client information | Shared workspace, customer-facing requests, normalized records, and an audit trail |

### Positioning guardrails

- FreightDoc is an **information and preparation** product—not a customs broker, importer of record, or legal filing service.
- Low-confidence HS classification, fallback tariff evidence, missing data, or critical validation findings must block “review ready” status and be explicit.
- “Generated” never means “filed,” “approved,” or “compliant.”

## 2. The product experience to build

### Core user journey: exporter

1. Create or select an organization and invite the colleague who owns trade review.
2. Create a shipment from a template, prior shipment, CSV import, or guided desk.
3. Select saved exporter/importer/consignee/product records; enter only shipment-specific values.
4. Upload source documents. FreightDoc extracts suggestions but never overwrites reviewed fields automatically.
5. Resolve a structured “missing information” checklist.
6. Run the preparation pipeline; see provenance, confidence, source freshness, and findings.
7. Fix, assign, comment on, or explicitly acknowledge non-blocking exceptions.
8. Submit for internal or broker review; the reviewer approves, rejects, or requests changes.
9. Generate a versioned dossier and share it through an expiring, access-controlled link.
10. Archive the completed shipment with its immutable activity history and exportable audit package.

### Core user journey: forwarder / broker

1. Create a client workspace or receive a client-submitted shipment.
2. Review the queue ordered by departure date, risk, missing data, and assignment.
3. Compare data from uploaded evidence against the shipment facts.
4. Mark findings as resolved, waived with a reason, or returned to the exporter.
5. Export the review-ready package for the filing system; filing remains outside FreightDoc until a compliant integration exists.

### Product information architecture

- **Home / operations dashboard:** shipment queue, urgent exceptions, team activity, saved views.
- **Shipment workspace:** Overview, Cargo & classification, Parties, Documents, Requirements, Review, Activity.
- **Dossier:** versioned PDF package, validation summary, source provenance, download/share controls.
- **Library:** products, parties, document templates, saved routes, broker contacts.
- **Organization settings:** users, roles, retention, integrations, billing, API keys/webhooks.

## 3. Prioritized SaaS epics

### P0 — required for a useful, paid pilot

| Epic | User value | Concrete scope | Done when |
|---|---|---|---|
| Organization workspace | Data belongs to the customer, not an individual login | Clerk organization mapping, organization ID on every tenant record, invite flow, owner/admin/member/reviewer roles | A member cannot read or mutate another organization’s shipment by URL/API guessing |
| Shipment lifecycle | Users can manage work over time | States: draft → collecting → processing → needs review → review ready → approved/returned → archived; owner, due date, tags, activity history | Every state change is attributable and a dossier is tied to a shipment version |
| Reusable data library | Repeated exports become faster | Product catalog, trade-party profiles, saved routes, default commercial terms | A new shipment can start from a product + parties without retyping core facts |
| Reliable document intake | Uploaded evidence becomes actionable safely | Existing strict sanitation, type-specific extraction, field confidence/provenance, user “apply suggestion” flow, retry/error visibility | No source file is retained unless a future storage policy explicitly opts in; suggestions never overwrite facts |
| Review and exception center | The team knows what prevents shipment preparation | Findings with severity, owner, due date, comments, resolution reason, blockers vs warnings | Critical findings block a readiness label and unresolved items appear in queue and dossier |
| Dossier versioning and sharing | Handoff is trustworthy | Immutable generated package version, PDF/ZIP download, expiring share links, revocation, access log | A recipient sees a named version and no link remains valid after revocation/expiry |
| Operational reliability | SaaS feels dependable | Background job status, retries/idempotency, error messages, service health, support correlation ID | Repeated clicks do not create duplicate dossiers and a failed job can be retried safely |
| Security baseline | Customers can trust the workspace | Tenant isolation tests, audit events, least-privilege roles, rate limits, encrypted secrets, retention/deletion controls | Security tests cover cross-tenant access and production logging omits sensitive document content |

### P1 — makes it a strong operations product

| Epic | User value | Concrete scope |
|---|---|---|
| Collaboration | Internal and broker teams can work in one place | Comments, @mentions, assignments, review requests, email notifications, decision log |
| Customer intake portal | Forwarders collect accurate client data without spreadsheet churn | Branded link, required fields, upload request, expiry, access token, submit-to-review |
| More useful product intelligence | Product history reduces classification risk | HS decision history, evidence notes, manual override with reason, classification comparison, confidence thresholds |
| Rules and content operations | Requirements evolve safely | Versioned rule sets, effective dates, jurisdiction/source metadata, changelog, staging/approval path |
| Integrations | FreightDoc fits existing workflows | Email import, CSV import/export, cloud storage connectors, webhooks, Zapier/Make; carrier/forwarder integrations only after validated demand |
| Analytics | Teams can prove impact | Lead time, exception rate, top missing fields, readiness by corridor, dossier volume, user adoption |
| Support tooling | Solo founder can support pilots | Admin-only support console with masked identifiers, job trace, feature flags, incident banner, data export request workflow |

### P2 — only after repeatable pilot demand

| Epic | Rationale | Guardrail |
|---|---|---|
| Public API and API keys | Enables ERP/WMS integrations | Stable versioning, scoped tokens, quotas, idempotency, audit log before launch |
| ERP/WMS connectors | Removes duplicate entry for larger customers | Build only for paid design partners and a narrow first connector |
| Multi-language and locale support | Necessary for global teams | Start with document language and date/currency localization, not automatic legal translations |
| Advanced approvals | Supports controlled operations | Configurable approval policies and e-signature integration; not a legal filing approval claim |
| Broker marketplace / filing workflows | Potential network effect | Requires legal, liability, onboarding, and support investment—do not ship as a solo-founder feature |
| Mobile companion | Useful for reviewing/uploading at a warehouse | Keep web PWA as the source of truth; no native app until sustained mobile demand |

## 4. Multi-tenant data and authorization design

### Tenancy model

Adopt an organization-first model. Clerk remains identity and session authority; Neon/Postgres stores application authorization and product data.

```text
Clerk user ID ──< OrganizationMembership >── Organization
Organization ──< Shipment ──< ShipmentVersion
Shipment ──< UploadedDocumentMetadata / ExtractedFact / Finding / DossierVersion / AuditEvent
Organization ──< Product / TradeParty / RouteTemplate / Integration
```

Every customer-owned row must contain `organization_id`. Repository queries must require it, composite indexes should start with it, and server-side authorization must never trust an organization ID provided only by the browser.

### Initial RBAC

| Role | Permissions |
|---|---|
| Owner | Billing, retention, integrations, members, all organization records |
| Admin | Members except owners, all shipment and library records |
| Preparer | Create/edit assigned or permitted shipments; submit for review |
| Reviewer | View organization shipments; resolve/reject/approve reviews; cannot change billing or roles |
| Viewer | Read shared shipments/dossiers only |

Use permission checks at the API/service layer, not UI visibility alone. Add per-shipment access only when real customer workflows require it; organization roles are sufficient for P0.

## 5. Billing and packaging

Start with a **paid-pilot model**, not self-serve complexity:

- **Pilot:** fixed monthly fee, limited organizations/users, concierge onboarding, a monthly shipment allowance.
- **Starter:** one organization, a small seat count, usage-based shipment/dossier allocation.
- **Team:** multiple reviewers, shared links, audit history, integrations, higher usage.
- **Broker/forwarder:** priced only after repeatable demand and multi-client workflows are validated.

Use Stripe Checkout + Billing Portal in P1. Store only Stripe customer/subscription identifiers and entitlements; never store card data. Meter *completed dossier attempts* and/or *active shipments*, not LLM tokens, so customer pricing is predictable. Enforce quotas server-side, show usage transparently, and grace-period rather than immediately delete data after payment failure.

## 6. Trust, privacy, and compliance posture

### Non-negotiable controls

- Retain the current upload limits: **15 MiB/file, 40 MiB/request, 10 files/request**, MIME/content validation, archive path protections, parser bounds, and formula-safe CSV extraction.
- Discard original bytes after in-memory extraction by default. Persist only metadata, extracted text/facts, confidence, errors, and explicit user decisions.
- Encrypt connections (TLS); use managed encryption at rest from Neon/Render/Vercel and never commit secrets.
- Keep an append-only application audit event for access, changes, pipeline runs, downloads, shares, reviewer decisions, and deletion requests.
- Minimize logs: correlation IDs and operational metadata only; redact extraction text, tokens, credentials, and sensitive trade-party identifiers.
- Implement account/organization export and deletion. Establish deletion propagation across database, share links, cached PDFs, and backups with documented timelines.
- Use signed, short-lived dossier downloads and expiring share links. No public directory or guessable object URLs.

### Compliance roadmap (do not overclaim)

P0: privacy notice, Terms, data-processing description, subprocessor list, retention controls, incident response playbook, backup/restore runbook.
P1: DPA, regional hosting decision, security questionnaire packet, annual access-review cadence, vulnerability/dependency monitoring.
P2: SOC 2 readiness only when enterprise demand justifies the operational overhead.

FreightDoc should never claim legal compliance. The interface should consistently label results as “review-ready information” and request broker/legal review for classifications below threshold or critical findings.

## 7. Integrations strategy

Prioritize in this order:

1. CSV import/export and inbox forwarding (fastest real-world adoption).
2. Storage export to customer-controlled Drive/SharePoint/Box, only after a retention/threat-model review.
3. Webhooks for shipment state, review request, dossier ready, and exception created.
4. One design-partner ERP/WMS connector, selected from actual pilot usage.
5. Carrier, forwarder, and customs filing providers only with written API contracts and liability review.

All integrations need OAuth/token encryption, scope minimization, clear disconnect/revoke controls, retry/idempotency behavior, and per-organization audit events.

## 8. UX quality bar

The visual system should remain FreightDoc: industrial editorial logistics, ink/navy, paper, signal orange, deliberate motion—not a generic dashboard.

Functional quality bar:

- Every screen answers “what needs attention, who owns it, and what happens next?” within a few seconds.
- Forms preserve drafts automatically, validate inline, support keyboard and touch use, and never lose unsaved typed data after a pipeline/API error.
- The shipment workspace uses progressive disclosure: core fields first, advanced commercial/cargo fields available when needed.
- Results map API data into document cards, source labels, readiness state, and actions—never raw JSON.
- Mobile is a first-class layout: safe touch targets, one-column forms, sticky action bar, accessible upload alternative, and no horizontal overflow.
- Animations are progressive enhancement. The cargo story must have a static/reduced-motion fallback and must never block entry to the workspace.
- Establish component states for loading, empty, error, offline, retry, success, and permission denied before adding new screens.

## 9. Architecture implications

### Keep now

- FastAPI service boundary, Pydantic validation, rule-based requirements, structured AI outputs, provenance, ReportLab generation, React/Vite PWA, Clerk, Neon/Postgres.

### Add in P0

- Organization and membership tables/migrations; a single authorization service.
- Shipment versioning and immutable dossier version metadata.
- Transactional job model for pipeline runs (`queued`, `running`, `failed`, `completed`, `cancelled`) with idempotency keys.
- A background worker/queue for long-running generation, extraction, and PDF assembly. Keep request API responsive and expose polling/SSE status.
- Object storage only for *generated* dossiers if inline base64 becomes too large; input originals remain discarded by policy.
- Central configuration for model provider, rule versions, retention, quotas, and feature flags.
- Observability: structured JSON logs, metrics (latency/error/fallback), tracing by correlation ID, uptime alerting, and an error tracker.

### Data quality controls

- Separate **extracted suggestion**, **user-entered fact**, **reviewed fact**, and **generated document field** records or lineage metadata.
- Require a reason for manual HS override, finding waiver, and rule exception.
- Capture rules version, tariff source/retrieval time/fallback status, model/provider/version, prompt schema version, and dossier version with each run.
- Do not silently change a historical generated document when rules/models change; generate a new dossier version.

## 10. Phased delivery plan for a solo founder

### Phase 0 — stabilize the existing product (1–2 weeks)

- Fix any blank/error states; test the complete signed-in journey locally and deployed.
- Ensure all user-facing results are componentized, accessible, and no API/JSON dumps remain.
- Baseline Sentry/equivalent error reporting, health checks, backup/restore notes, and a support email path.
- Recruit 3–5 design partners in a single corridor/use case.

**Exit:** a pilot user can create a shipment, upload evidence, run the pipeline, view findings, and download a dossier without founder intervention.

### Phase 1 — pilot operations (3–5 weeks)

- Organization workspaces/RBAC, shipment lifecycle, activity log, saved parties/products/routes, draft recovery.
- Review queue, comments, assignments, versioned dossiers, expiring links.
- Landing-page conversion flow, product onboarding, sample shipment, and basic product analytics.

**Exit:** a small team can prepare and review recurring shipments while maintaining ownership boundaries and an auditable history.

### Phase 2 — paid validation (4–6 weeks)

- Stripe billing/entitlements, usage limits, customer/admin settings, export/delete flows.
- Customer intake links, CSV import/export, webhooks, reportable operations analytics.
- Rule/content review process and source freshness monitoring.

**Exit:** 3–10 paid customers or paid pilots use FreightDoc monthly and at least one measurable outcome improves (preparation time, missing-field rate, or rework rate).

### Phase 3 — scale only from evidence (ongoing)

- One high-demand integration, richer approval policy, more corridors, and benchmarked classification quality.
- Improve job throughput, resilience, and support operations before pursuing enterprise compliance or a marketplace.

## 11. Product metrics and rollout gates

### North-star metric

**Review-ready dossiers per active organization per month**, accompanied by an explicit human-review outcome.

### Supporting metrics

- Activation: first successful draft and first dossier within seven days.
- Time to review-ready dossier.
- Percentage of shipments with a critical finding before generation/review.
- Findings resolved without external support.
- Classification confidence distribution and manual override rate.
- Extraction suggestion acceptance rate (never measured as correctness without review).
- Dossier regeneration/rework rate.
- Weekly active organizations, retained organizations, and paid conversion.
- Pipeline success rate, p95 duration, tariff fallback rate, and document-parser failure rate.

Do not optimize for “documents generated” alone; that can incentivize unsafe automation.

## 12. Acceptance criteria before calling FreightDoc a SaaS product

### Product and UX

- A newly invited user can complete onboarding and create a review-ready pilot shipment without a live walkthrough.
- Users can save/resume drafts and reuse products/parties.
- Every finding has severity, evidence/provenance, owner, status, and next action.
- A generated dossier always identifies shipment, organization, version, rules/source information, date, and disclaimer.
- Desktop, tablet, mobile, keyboard-only, and reduced-motion experiences are tested for core flows.

### Security and reliability

- Tenant-isolation tests prevent cross-organization reads/writes/downloads/shares.
- No original upload bytes are persisted under the default policy.
- Rate/upload limits, malformed-file tests, auth failures, retry/idempotency, and deletion flows are automated.
- Production dashboards alert on pipeline failures and high fallback/parser failure rates.
- Restore procedure is tested before paid customer data is accepted.

### Commercial readiness

- Pricing, limits, support channel, privacy notice, terms, retention policy, and “not legal advice” language are live.
- Pilot onboarding checklist and a 30-minute support/review playbook exist.
- At least three design partners validate the chosen ICP before expanding corridor coverage or integrations.

## 13. Explicitly deferred scope

- Acting as customs broker, legal advisor, importer/exporter of record, or filing directly with customs agencies.
- A marketplace, real-time shipment tracking, freight booking, payments for duties, or carrier rate shopping.
- Broad global corridor coverage before data quality, rule management, and support capacity are proven.
- Native mobile apps, AI auto-approval, autonomous field overwrites, and opaque “compliance guaranteed” scores.
- Enterprise SSO/SCIM, multi-region active-active infrastructure, and SOC 2 certification until there is funded demand.

## 14. Principal risks and mitigations

| Risk | Mitigation |
|---|---|
| Incorrect classification or rules cause harmful reliance | Confidence thresholds, source evidence, human review gates, controlled overrides, explicit disclaimers |
| Tariff/rule data is stale or unavailable | Provenance/time stamps, fallback label, freshness monitoring, versioned rules, no claim that fallback is a current duty quote |
| AI hallucination or data mismatch | Structured schemas, deterministic requirements, cross-validation, field lineage, retry/error handling, reviewer approval |
| Scope creep overwhelms a solo founder | One ICP/corridor, paid design partners, phased gates, no custom integration without commitment |
| Sensitive commercial data exposure | Tenant authorization, minimal retention, no raw-original storage, redacted logs, signed sharing, security tests |
| Free tiers become unreliable at pilot scale | Document resource limits, queueing, observability, clear migration triggers to paid managed services |

## 15. Decision log for the next implementation cycle

1. Validate the first paid-pilot ICP: recurring SME exporter vs. forwarder/broker team.
2. Decide whether Clerk Organizations is the identity source for organizations or whether the application owns organization membership while mapping Clerk users.
3. Choose a job queue/provider compatible with the current Render/Neon budget and deploy model.
4. Define retention duration for extracted text and generated dossiers with pilot customers before enabling external sharing.
5. Select one corridor and a small, auditable document-rule set as the “quality bar” before expanding coverage.

Until these decisions are validated, implement only Phase 0 reliability work and P0 foundations—not P1/P2 integrations or marketplace ideas.
