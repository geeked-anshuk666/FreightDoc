# System overview

FreightDoc creates a reviewable export-documentation dossier from shipment facts. It is informational preparation software, not a broker, filing, clearance, sanctions-screening, or legal service. Human review is required for consequential decisions.

## Product flow

1. A signed-in owner creates a shipment and optionally submits bounded source documents.
2. Deterministic rules resolve the supported corridor and required documents; classification/tariff evidence carries source or fallback labels.
3. The product generates draft documents, validation findings, and a PDF dossier.
4. Owners review facts, revisions, quality findings, and suggestions; acceptance/rejection/waiver is attributable.

The `/api/v1` surface adds canonical records, revisions, review tasks, quality findings, local rules/playbooks/rulings, scenarios, operations, and governance. Connector and regulated-action surfaces are manual/mock only unless an approved live integration is explicitly configured.

## Data and safety

Workspace data is owner-scoped with the opaque Clerk subject. Original upload bytes are processed transiently and must not be logged, cached, or persisted. Deterministic processing works without a provider key; optional runtime AI suggestions cannot make authoritative decisions. See the [safety contract](deterministic_ai_safety_contract.md), [security architecture](security_architecture.md), and [known tradeoffs](known_tradeoffs.md).
