# FreightDoc

Generate compliant export documentation in 90 seconds. Built with Codex
and GPT-5.6 for OpenAI Build Week 2026.

## What This Is
FreightDoc classifies a product's HS code, retrieves tariff data,
generates a complete export document package, cross-validates it for
consistency and destination-specific compliance gaps, and renders
downloadable PDFs — all in under 90 seconds.

## Documentation Map

### Public documentation (`docs/`)
| File | What it covers |
|---|---|
| `system_overview.md` | Plain-English walkthrough of the whole system |
| `codebase_explained.md` | File-by-file map of the codebase |
| `design_decisions.md` | Why things were built the way they were |
| `project_concepts.md` | Core UX/domain metaphors (traffic-light severity, document folder) |
| `scaling_to_1_billion_users.md` | How this would scale beyond the hackathon MVP |
| `api_reference.md` | Every endpoint, request/response shape |
| `hld.md` / `lld.md` | High-level and low-level design |
| `database_design.md` | Current stateless design + future schema |
| `security_architecture.md` | Security posture and controls |
| `testing_strategy.md` | What's tested and how |
| `deployment_guide.md` | How to deploy from scratch |
| `uml_diagrams.md` / `class_diagrams.md` / `entity_relationships.md` | Diagrams |
| `troubleshooting_guide.md` | Common failure modes and fixes |
| `implementation_notes.md` | Exact prompts and implementation details |
| `interview_defense_guide.md` | How to explain this project in an interview |
| `known_tradeoffs.md` / `what_we_skipped_and_why.md` | Explicit scope decisions |
| `future_improvements.md` / `feature_prioritization.md` | Roadmap |

### Private documentation (`.private_docs/`, git-ignored)
Interview-prep and deep-dive material: `project_brain.md`,
`line_by_line_explanation.md`, `interviewer_questions.md`,
`system_deep_dive.md`, `code_walkthrough.md`, `architecture_rationale.md`,
`database_rationale.md`, `api_rationale.md`, `security_rationale.md`,
`scaling_rationale.md`.

## Onboarding Process (for a new developer)
1. Read this README fully.
2. Read `docs/system_overview.md` for the plain-English mental model.
3. Read `docs/hld.md` then `docs/lld.md` for architecture depth.
4. Read `docs/api_reference.md` while running the app locally.
5. Skim `docs/known_tradeoffs.md` to understand what's intentionally
   unfinished and why.
6. You should be productive (able to make a safe change) within a few
   hours having read only the above.

## Setup
```bash
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
cd frontend && npm install && npm run dev
```

## Tech Stack
Python/FastAPI backend, React/Vite/Tailwind PWA frontend, GPT-5.6 Luna
(runtime) / Terra (built with Codex), USITC HTS / UN Comtrade / EU TARIC
for trade data.

## How Codex Was Used
[To be filled in with specifics once the build session is complete —
must be written by hand, not AI-generated prose, per hackathon rules.]

Codex Session ID: [from `/feedback`]
