# FreightDoc — plan.md

## Phase 0 — Setup (Day 1 morning)
- [ ] Scaffold backend (FastAPI project structure per architecture.md)
- [ ] Scaffold frontend (Vite + React + Tailwind + vite-plugin-pwa)
- [ ] Confirm OpenAI API key + GPT-5.6 Luna/Terra access
- [ ] **Docs**: Create empty `docs/` and `.private_docs/` folder structure
      matching the full required tree; add `.private_docs/` to
      `.gitignore`.

## Phase 1 — Classification + Tariff (Day 1)
- [ ] Implement `POST /api/classify` (GPT-5.6 Luna, CLASSIFY_PROMPT)
- [ ] Implement `services/hts_api.py`, `services/tariff_api.py`
- [ ] Implement hardcoded fallback tariff dataset for the 8 launch
      corridors
- [ ] **Docs**: `docs/api_reference.md` (classify endpoint),
      `.private_docs/api_rationale.md` (why USITC + Comtrade + TARIC),
      `docs/design_decisions.md` (fallback dataset rationale)

## Phase 2 — Document Requirements + Generation (Day 1-2)
- [ ] Implement `data/country_rules.json` rule engine
      (`services/doc_engine.py`)
- [ ] Implement `POST /api/generate` (GPT-5.6 Luna, DOCUMENT_PROMPT)
- [ ] **Docs**: `docs/lld.md` (Pydantic models), `docs/entity_relationships.md`
      (conceptual ERD), `.private_docs/architecture_rationale.md`
      (rule engine vs. LLM decision)

## Phase 3 — Cross-Validation (Day 2)
- [ ] Implement `POST /api/validate` (GPT-5.6 Luna, VALIDATE_PROMPT)
- [ ] Implement `POST /api/full-pipeline` orchestrating all 6 steps
- [ ] **Docs**: `docs/hld.md`, `docs/uml_diagrams.md` (sequence diagram),
      `docs/known_tradeoffs.md` (what the validator does and doesn't
      catch)

## Phase 4 — PDF Rendering + Frontend (Day 2)
- [ ] Implement `services/pdf_generator.py` (ReportLab)
- [ ] Build ShipmentForm, PipelineProgress, DocumentTabs, ErrorPanel,
      WarningPanel, DownloadBar
- [ ] Wire PWA manifest + service worker
- [ ] **Docs**: `docs/codebase_explained.md` (frontend component map),
      `docs/testing_strategy.md` (what's tested vs. not)

## Phase 5 — Testing + Hardening (Day 2-3)
- [ ] Unit tests: rule engine, PDF generator
- [ ] Integration test: `/api/full-pipeline` against mocked externals
- [ ] Manual test: all 8 corridors produce sane output
- [ ] **Docs**: `docs/testing_strategy.md` (finalize), `docs/security_architecture.md`,
      `.private_docs/security_rationale.md`

## Phase 6 — Deployment (Day 3)
- [ ] Dockerfile for backend, deploy to Railway
- [ ] Deploy frontend to Vercel
- [ ] Verify PWA installability
- [ ] **Docs**: `docs/deployment_guide.md`, `.private_docs/architecture_rationale.md`
      (deployment topology decisions)

## Phase 7 — Documentation Completion + Review (Day 3)
- [ ] Generate remaining `docs/*`: `system_overview.md`,
      `project_concepts.md`, `scaling_to_1_billion_users.md`,
      `troubleshooting_guide.md`, `implementation_notes.md`,
      `interview_defense_guide.md`, `future_improvements.md`,
      `feature_prioritization.md`, `what_we_skipped_and_why.md`
- [ ] Generate remaining `.private_docs/*`: `project_brain.md`,
      `line_by_line_explanation.md`, `interviewer_questions.md`,
      `system_deep_dive.md`, `code_walkthrough.md`,
      `database_rationale.md`, `scaling_rationale.md`
- [ ] **Validation step**: confirm every doc is specific to FreightDoc
      (not generic filler) and cross-references actual code paths

## Phase 8 — Demo + Submission (Day 3-4)
- [ ] Record demo video per `05_DEMO_SCRIPT.md`
- [ ] Run `/feedback` in Codex, capture Session ID
- [ ] Finalize `README.md` and `CHANGELOG.md`
- [ ] Submit on Devpost

## Documentation Review & Validation Checklist (applies to every phase)
- [ ] Does every touched file have a corresponding doc update?
- [ ] Is `.private_docs/` still git-ignored?
- [ ] Does `CHANGELOG.md` have an entry for this phase?
- [ ] Are all production-readiness items from PRD.md Section 9 addressed
      (implemented or explicitly justified) somewhere in `docs/known_tradeoffs.md`?
