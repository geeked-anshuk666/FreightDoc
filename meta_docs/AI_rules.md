# FreightDoc — AI_rules.md

## 1. Model Usage Rules
- **Codex build sessions**: GPT-5.6 Terra, always. Do not switch models
  mid-session without a documented reason in `.private_docs/project_brain.md`.
- **Runtime classification, generation, validation**: GPT-5.6 Luna,
  always. Never call a heavier/more expensive model at runtime for these
  three tasks — they are well within Luna's capability and cost profile.
- **AI is never used where deterministic code can do the job.** Tariff
  lookup, document-requirements matrix, and PDF rendering are code, not
  prompts. This rule is non-negotiable and must be enforced in code
  review (see `docs/design_decisions.md` for the rationale).

## 2. Prompt Discipline
- Every prompt must request **structured JSON output** — no free-form
  prose parsing in the critical path.
- Every prompt must be version-controlled as a named constant
  (`CLASSIFY_PROMPT`, `DOCUMENT_PROMPT`, `VALIDATE_PROMPT`) in
  `services/openai_client.py` or an adjacent prompts module — never
  inlined ad hoc at the call site.
- Every prompt change must be logged in `CHANGELOG.md` under an "AI
  Behavior Changes" subsection.

## 3. Documentation-First Development (MANDATORY)
- No feature is merged/considered complete until its corresponding
  `docs/*` entry exists and is accurate.
- No architectural decision is made without a corresponding entry in
  `.private_docs/architecture_rationale.md` (or the relevant rationale
  file) in the same work session.
- Every new external API integration requires a `.private_docs/
  api_rationale.md` entry before the integration is considered done.

## 4. Mandatory Documentation Updates Per Change Type
| Change type | Required doc update |
|---|---|
| New/changed endpoint | `docs/api_reference.md`, `docs/lld.md` |
| New/changed prompt | `docs/implementation_notes.md`, `CHANGELOG.md` |
| New/changed Pydantic model | `docs/lld.md`, `docs/class_diagrams.md` |
| New/changed external API integration | `.private_docs/api_rationale.md` |
| New/changed security control | `docs/security_architecture.md`, `.private_docs/security_rationale.md` |
| New/changed scaling approach | `docs/scaling_to_1_billion_users.md`, `.private_docs/scaling_rationale.md` |
| Any tradeoff/scope cut | `docs/known_tradeoffs.md`, `docs/what_we_skipped_and_why.md` |

## 5. Changelog Update Requirements
Every commit that changes behavior (not pure refactor) must have a
corresponding `CHANGELOG.md` entry categorized as: Added / Changed / Fixed
/ Security / Documentation.

## 6. Docs Synchronization Requirement
Before considering any `plan.md` phase complete, the coding agent must run
a self-check: "Does every file I touched in this phase have an accurate
reflection in `docs/*` or `.private_docs/*`?" If no, the phase is not
complete.

## 7. AI Output Validation Rules
- All structured JSON output from GPT-5.6 Luna must be validated against
  the corresponding Pydantic model before use. Malformed output triggers
  a single retry, then a graceful error surfaced to the user — never a
  silent failure or a crash.
- The cross-validator's output must never be presented as an automatic
  block on shipping without a human-readable "why" — every error must
  include the `fix` field, no bare error codes.
