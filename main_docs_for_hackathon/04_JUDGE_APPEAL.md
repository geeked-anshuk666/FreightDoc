# FreightDoc — 04_JUDGE_APPEAL.md

## Why judges will care (mapped to the 4 judging criteria)

### Technological Implementation
- A real 6-step agentic pipeline: classify → tariff lookup → rule-based
  document-requirements engine → generate → cross-validate → render.
- Combines LLM reasoning (classification, generation, validation) with
  deterministic systems (rule engine, PDF rendering, live public APIs) —
  demonstrates judgment about *where* to use AI and where not to, which is
  exactly what mature technical implementation looks like.
- The cross-validator is a genuinely non-trivial reasoning task (multi-
  document consistency + destination-specific compliance) — not a wrapper
  around a single prompt.

### Design
- Live pipeline-progress UI, tabbed document viewer, color-coded error
  severity (critical vs. warning), before/after compliance score — visually
  legible in seconds, which matters enormously in a 3-minute demo.

### Potential Impact
- A single missing document costs real exporters real money (fines,
  week-long shipment holds) — this is quantifiable, not abstract.
- Serves an underserved segment: the long tail of small/mid exporters priced
  out of both human forwarders and enterprise software.

### Quality of Idea
- Not "another AI form-filler." The insight — that generation without
  cross-validation is not a usable product for anything with financial/legal
  consequences — is the kind of domain understanding judges are explicitly
  told to reward over novelty-for-its-own-sake.

## Standing-ovation demo beat
The moment the red error panel appears reading *"CE Declaration required for
electronics entering EU — missing from package. This will cause customs
hold at Frankfurt,"* followed immediately by that document being generated
and the compliance score jumping from 71 to 94. That is the single frame a
judge will remember.
