# FreightDoc — ui_ux_brief.md

## 1. Design Principles
- **Legibility over decoration.** A judge or a real user must understand
  the state of their shipment (compliant / not compliant) within 2
  seconds of looking at the screen.
- **Color-coded severity.** Critical errors: red. Warnings: amber.
  Compliant/success: green. No other color is used for status
  communication, to keep the system unambiguous.
- **Progress transparency.** The 6-step pipeline is not a spinner — each
  step is individually visible and animates in sequence, so the user (and
  a demo audience) understands what is happening and why it takes ~15-20
  seconds.

## 2. Visual Language
- Dark, professional palette (`#0f172a` background, `#3b82f6` accent) —
  appropriate for a trade/logistics professional tool, not a consumer
  toy.
- Tabbed document viewer mimics a physical document folder metaphor —
  familiar to the target user (exporters used to reviewing paper
  documents).
- Compliance score rendered as a large animated number that visibly moves
  (e.g., 71 → 94) when an error is fixed, reinforcing the "we caught this
  before you shipped" value proposition.

## 3. Key Components
| Component | Behavior |
|---|---|
| ShipmentForm | Single-page form, inline validation, no multi-step wizard (reduces friction for a fast demo and a busy exporter) |
| PipelineProgress | 6 discrete steps, each with a loading/success/error state icon |
| DocumentTabs | One tab per document type, PDF preview inline, individual download button per tab |
| ErrorPanel | Red, top-of-results placement, one row per critical error with an inline "fix" action where automatable |
| WarningPanel | Amber, below ErrorPanel, dismissible per warning |
| DownloadBar | Sticky footer, "Download All (ZIP)" primary action |

## 4. Accessibility Baseline
- All color-coded status indicators must also carry a text label or icon
  (never color alone) to remain usable for colorblind users.
- All interactive elements keyboard-navigable; form fully usable without
  a mouse.

## 5. Design Documentation Requirements (Mandatory for Stage 2)
- `docs/project_concepts.md` must explain the "document folder" and
  "traffic light severity" metaphors as core UX concepts a new engineer
  needs to understand before touching the frontend.
- `docs/design_decisions.md` must justify the choice of a single-page
  form over a multi-step wizard, and the choice to animate the compliance
  score rather than show it statically.

## 6. Component Documentation Requirements
- Every component in Section 3's table must be documented in
  `docs/lld.md` with its exact props interface.
- `.private_docs/code_walkthrough.md` must include the reasoning behind
  the PipelineProgress component's design — specifically, why each step
  is shown individually rather than a single aggregate loading state
  (answer: builds user trust and gives a natural demo narration beat).
