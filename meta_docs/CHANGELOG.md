# FreightDoc — CHANGELOG.md

All notable changes to this project are documented here. Entries are
categorized as **Added / Changed / Fixed / Security / Documentation**.

Every entry that touches code, architecture, schema, API surface, or
security MUST have a corresponding documentation update in the same
change — this changelog is also the audit trail proving that
synchronization happened.

## [Unreleased]

### Documentation
- Implementation reconciliation (2026-07-20): the executable backend currently
  uses configuration-driven Groq defaults and owner-scoped Clerk/Neon support.
  Earlier model/stateless references in this planning set remain historical
  requirements; current behaviour is documented in the root `CHANGELOG.md` and
  `docs/implementation_notes.md` rather than being silently misrepresented.

### Changed
- Runtime AI is Groq (`llama-3.3-70b-versatile`) for classification, generation, and validation; Codex remains build-only.
- Tariff retrieval now separates USITC and UN Comtrade public-v1 services with concurrent orchestration and fallback data.

### Added
- FastAPI backend scaffold with structured AI stages, deterministic tariff/rule/PDF services, fallbacks, and tests.
- Backend API, architecture, deployment, security, testing, and rationale documentation.

### Changed
- Document generation uses `gpt-4o-mini`; classification and validation use `gpt-5.6-luna`.

### Added
- (placeholder — populate as Phase 0-8 of `plan.md` execute)

### Changed
- (placeholder)

### Fixed
- (placeholder)

### Security
- (placeholder)

### Documentation
- (placeholder — every `docs/*` and `.private_docs/*` file creation/update
  gets its own line here, referencing which code change it corresponds to)

## Update Requirements (policy, not history)
This file must be updated for:
- Every code change (feature, fix, refactor with behavioral impact)
- Every architecture change (new component, changed data flow)
- Every schema change (even conceptual/deferred schema changes documented
  in `backend_schema.md`)
- Every API change (new endpoint, changed request/response shape)
- Every documentation change (new doc file, substantive rewrite of an
  existing one)
- Every security change (new control, changed auth/validation behavior)

A phase in `plan.md` is not complete until its `CHANGELOG.md` entries
exist.
