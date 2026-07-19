# FreightDoc — 05_DEMO_SCRIPT.md

## 3-minute demo, beat by beat

### 0:00–0:25 — The problem (25s)
"Every year, tens of thousands of small exporters pay $500 to $2,000 per
shipment just for customs paperwork. A single missing document can hold your
cargo at the border for a week and cost over $10,000 in fines. FreightDoc
generates the complete documentation package in 90 seconds — and catches the
errors before you ship."

### 0:25–1:45 — Live demo (80s)
1. Type: "500 units of wireless Bluetooth earbuds, retail packaged."
2. Select: United States → Germany.
3. Declared value: $25,000 · Quantity: 500.
4. Hit Generate — show the pipeline progress steps running live (classify →
   tariff → requirements → generate → validate).
5. Four documents appear in tabs: Commercial Invoice, Packing List,
   Certificate of Origin, Customs Declaration.
6. Red error panel appears: "CE Declaration required for electronics
   entering EU — missing from package. This will cause customs hold at
   Frankfurt."
7. Click "Generate CE Declaration" — it's added to the package.
8. Compliance score animates from 71 → 94.
9. Click "Download All" → ZIP file downloads.

### 1:45–2:15 — Global scope (30s)
"FreightDoc supports 8 major trade corridors today, covering some of the
highest-volume global trade lanes. The document-requirements engine knows
the specific compliance rules for each destination — CE marking for EU
electronics, BIS certification flags for India, PSE marks for Japan."

### 2:15–2:45 — How Codex built this (30s)
Screen-record 30 seconds of the actual Codex build session — the pipeline
being scaffolded, a real prompt, the validation logic being written. "The
entire backend pipeline was built in Codex using GPT-5.6."

### 2:45–3:00 — Close (15s)
"FreightDoc: from product description to compliant documentation in 90
seconds. Available as a PWA — works on any device, anywhere."

## Presentation notes
- Rehearse the timing out loud at least 3 times before recording.
- Have the demo pre-warmed (run it once before recording so caches are hot
  and there's no visible lag).
- If the API is flaky on demo day, have a pre-recorded fallback clip ready.
