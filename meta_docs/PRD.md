# FreightDoc — Product Requirements Document (PRD.md)

## 1. Product Summary
FreightDoc is an agentic export-documentation generator. A user describes a
product in plain English, selects an origin/destination country pair, and
the system classifies the HS code, retrieves tariff data, determines
required documents, generates the full document package, cross-validates
it for internal consistency and destination-specific compliance gaps, and
renders downloadable PDFs — end to end in under 90 seconds.

## 2. Problem Statement
Small and mid-size exporters spend $500–$2,000 per shipment on manual
documentation, and a single missing or inconsistent document can hold cargo
at the border for days and trigger fines exceeding $10,000. No existing
tool both generates AND cross-validates a full document package against
itself and against destination-specific compliance rules.

## 3. Target Users
- Primary: small/mid e-commerce exporters and DTC brands shipping
  internationally, occasionally or at growing volume.
- Secondary: freight forwarders and customs brokers who would use this as
  an internal acceleration tool.
- Tertiary: manufacturers exporting equipment/components without an
  in-house trade compliance team.

## 4. Goals (Hackathon Scope)
- G1: Classify a product description into a defensible HS code with a
  confidence score.
- G2: Retrieve real tariff/duty data for a supported country pair.
- G3: Determine the correct required-document set via a deterministic rule
  engine (not LLM guesswork).
- G4: Generate a complete, internally consistent document package.
- G5: Cross-validate the package and surface a compliance score plus
  actionable error list.
- G6: Render all documents as downloadable PDFs.
- G7: Ship as an installable PWA.

## 5. Non-Goals (Hackathon Scope)
- Multi-user accounts / persistent company profiles (post-hackathon).
- Payment processing.
- Real customs-broker-of-record legal filing integration.
- Coverage beyond the 8 launch trade corridors.

## 6. Success Metrics
- Full pipeline (`/api/full-pipeline`) completes in under 20 seconds for a
  demo-representative request.
- Cross-validator reliably catches at least 3 distinct error classes
  (missing destination-specific document, value mismatch, quantity
  mismatch) across test fixtures.
- PWA installable on at least one mobile and one desktop browser.

## 7. Users Stories
- As an exporter, I want to describe my product in plain English and get a
  correct HS code so I don't have to hire a classification specialist.
- As an exporter, I want to see every document required for my specific
  destination country and product category so I don't miss anything.
- As an exporter, I want the system to tell me BEFORE I ship if something
  is wrong, not after customs rejects my shipment.

## 8. DOCUMENTATION REQUIREMENTS (MANDATORY)

This PRD mandates that the coding agent (Stage 2) produce the full
documentation tree defined below. This is a first-class deliverable, not
an afterthought — a phase is not "done" until its corresponding
documentation exists and is synchronized with the code.

### Required `docs/*` (public documentation)
docs/system_overview.md
docs/codebase_explained.md
docs/design_decisions.md
docs/project_concepts.md
docs/scaling_to_1_billion_users.md
docs/api_reference.md
docs/hld.md
docs/lld.md
docs/database_design.md
docs/security_architecture.md
docs/testing_strategy.md
docs/deployment_guide.md
docs/uml_diagrams.md
docs/class_diagrams.md
docs/entity_relationships.md
docs/troubleshooting_guide.md
docs/implementation_notes.md
docs/interview_defense_guide.md
docs/known_tradeoffs.md
docs/future_improvements.md
docs/feature_prioritization.md
docs/what_we_skipped_and_why.md

### Required `.private_docs/*` (git-ignored, interview/deep-dive prep)
.private_docs/project_brain.md
.private_docs/line_by_line_explanation.md
.private_docs/interviewer_questions.md
.private_docs/system_deep_dive.md
.private_docs/code_walkthrough.md
.private_docs/architecture_rationale.md
.private_docs/database_rationale.md
.private_docs/api_rationale.md
.private_docs/security_rationale.md
.private_docs/scaling_rationale.md
`.private_docs/` MUST be added to `.gitignore` immediately upon creation.

### Documentation objectives
1. A developer who has never seen this project must become productive
   within a few hours using only `docs/*`.
2. The original author must be able to defend every design, database,
   security, and scaling decision in an interview setting using only
   `.private_docs/*`.
3. Documentation and code must never drift — every PR/change that touches
   architecture, schema, API surface, or security must update the
   corresponding doc in the same change.

### Knowledge transfer requirements
- Every external API integration (USITC HTS, UN Comtrade, EU TARIC) must
  have a corresponding rationale entry in `.private_docs/api_rationale.md`
  explaining why it was chosen and what was rejected.
- Every prompt used in the AI pipeline must be documented in
  `docs/implementation_notes.md` with its exact text and purpose.
- Every production-readiness item (see Section 9) must be explicitly
  addressed — implemented, or explicitly deferred with written
  justification — in `docs/known_tradeoffs.md` and
  `docs/what_we_skipped_and_why.md`.

## 9. Production Readiness Evaluation (Mandatory — Nothing Silently Omitted)

For every category below, the coding agent must either implement it or
explicitly document why it is unnecessary at this project's current scale,
in `docs/known_tradeoffs.md` and the relevant rationale file under
`.private_docs/`.

- **Database**: FreightDoc's MVP is stateless per request (no persistent
  user data). Document explicitly in `.private_docs/database_rationale.md`
  why no database is used yet, and what the schema would look like once
  company profiles/shipment history are added (see `backend_schema.md`
  for the deferred schema).
- **Caching**: HS classification results should be cached (same product
  description → same code) to reduce latency and AI cost. Document cache
  key strategy, TTL, and invalidation in `docs/scaling_to_1_billion_users.md`.
- **Reliability**: External API calls (USITC, UN Comtrade, EU TARIC) must
  have retry with exponential backoff and a hardcoded fallback tariff
  dataset for the 8 launch corridors so a flaky public API never breaks
  the demo or a real user's session.
- **Performance**: The 6-step pipeline should support async/parallel
  execution where steps are independent (e.g., tariff retrieval from
  multiple sources can run concurrently).
- **Security**: No user authentication exists in the MVP (stateless,
  no accounts) — this must be explicitly justified in
  `.private_docs/security_rationale.md`, along with the plan for adding
  auth when persistence is introduced. Input validation on all
  user-supplied fields (product description, declared value, quantity) is
  mandatory regardless.
- **Observability**: Structured logging with request correlation IDs
  across the 6-step pipeline is required so a failed classification or
  validation step can be traced end to end.
- **Scalability**: Document the horizontal scaling path (stateless
  FastAPI instances behind a load balancer) even though the hackathon
  deployment is single-instance on Railway.
- **Deployment**: Dockerfile, environment variable management via `.env`
  (never committed), and a documented rollback procedure are mandatory
  even for the MVP deployment.
- **Testing**: At minimum, unit tests for the rule engine (document
  requirements matrix) and the PDF renderer, plus integration tests for
  `/api/full-pipeline` against mocked external APIs.

## 10. Acceptance Criteria
- All 10 Stage 1 planning docs exist and cross-reference the documentation
  requirements above.
- All 22 `docs/*` and `.private_docs/*` files exist after Stage 2 and are
  non-empty, substantive, and specific to FreightDoc (not generic
  boilerplate).
- `.private_docs/` is git-ignored.
- Every production-readiness item in Section 9 is either implemented or
  explicitly justified as deferred, with the justification traceable to
  `docs/known_tradeoffs.md`.
