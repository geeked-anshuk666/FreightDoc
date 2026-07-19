# FreightDoc — 03_WHY_NOW.md

## Why this becomes possible today, not two years ago

1. **HS classification quality.** Classifying a product description into a
   correct 6-digit (or deeper) HS code requires understanding both the
   physical nature of the product and the legal taxonomy of the HS
   nomenclature. GPT-5.6-class models can read a plain-English description
   and output a defensible classification with a confidence score — a task
   that required a licensed customs broker as recently as 18 months ago.

2. **Structured multi-document generation in one pass.** Generating four
   internally-consistent documents (commercial invoice, packing list,
   certificate of origin, customs declaration) that all agree with each
   other on value, quantity, and origin requires the model to hold and
   reuse a consistent set of facts across a long structured output — this
   is now reliable with JSON-mode structured outputs on frontier models.

3. **Cross-document validation as a reasoning task.** Spotting "your invoice
   says 500 units, your packing list says 480" or "you're missing the CE
   Declaration required for this destination + category" requires the model
   to reason over multiple documents simultaneously and apply
   destination-specific compliance logic — a genuinely new reasoning
   capability at accessible cost and latency.

4. **Free, public, live trade data infrastructure exists today.** USITC's
   HTS REST API, UN Comtrade, and EU TARIC are all public, free, and
   queryable in real time — the data layer this idea depends on didn't
   need to be built; it already exists and is stable.

5. **Global trade friction is actively increasing, not decreasing**, which
   makes the underlying pain more acute this year than in prior years —
   tariff schedules, country-of-origin rules, and compliance requirements
   change frequently enough that manual tracking is increasingly untenable
   for small exporters.
