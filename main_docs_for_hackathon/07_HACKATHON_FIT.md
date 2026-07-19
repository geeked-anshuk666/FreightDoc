# FreightDoc — 07_HACKATHON_FIT.md

## Track
Work & Productivity.

## Required technologies, used correctly (not bolted on)
- **Codex**: used throughout the build (not just at the start) — scaffolding
  the FastAPI backend, writing the rule engine, writing the validation
  prompt logic, writing the PDF renderer, iterating on the frontend.
- **GPT-5.6**: used at runtime for the three reasoning-heavy steps
  (classification, generation, cross-validation) where a rule engine alone
  cannot do the job — while everything that *can* be deterministic (tariff
  lookup, document-requirements matrix, PDF rendering) deliberately is not
  routed through the model. This demonstrates judgment, not "AI for AI's
  sake," which is explicitly what the judging rubric rewards.

## Judging rubric alignment
| Criterion | How FreightDoc scores |
|---|---|
| Technological Implementation | Multi-step agentic pipeline with reasoning + deterministic stages, integrating 3 free public trade-data APIs |
| Design | Clear pipeline-progress UI, color-coded errors, before/after compliance score |
| Potential Impact | Real, quantifiable financial pain ($10K+ fines, week-long holds) for a large underserved segment |
| Quality of Idea | The cross-validation insight is the differentiator vs. every "AI fills a template" competitor |

## Submission requirements checklist alignment
- Session ID captured via `/feedback` before closing the primary Codex thread.
- README written by hand (not AI-generated prose) documenting exactly how
  Codex and GPT-5.6 were used at each stage.
- Repo shared appropriately if private.
