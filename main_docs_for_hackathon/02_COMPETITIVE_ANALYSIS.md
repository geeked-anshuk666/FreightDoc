# FreightDoc — 02_COMPETITIVE_ANALYSIS.md

## Existing solution categories and why each falls short

### 1. Freight/logistics platforms (Flexport, ShipBob, Freightos)
- Core product is booking freight and tracking shipments in transit.
- Documentation is either an afterthought or requires manual upload of
  pre-existing correct documents — they don't generate or validate them.
- Pricing and onboarding assumes a certain shipping volume; not built for a
  first-time or occasional exporter.

### 2. Enterprise trade compliance software (Amber Road, Thomson Reuters ONESOURCE Global Trade, MIC Customs Solutions)
- Genuinely powerful, but **$30,000+/year**, multi-month implementation,
  built for large enterprises with dedicated trade compliance teams.
- Completely inaccessible to the long tail of small/mid exporters who are
  the majority of cross-border e-commerce volume.

### 3. Human freight forwarders / customs brokers
- $500–$2,000 per shipment.
- Still manual — a human is filling out templates and eyeballing
  consistency. Errors happen because no forwarder is running an automated
  cross-document consistency check on every field, every time.
- Turnaround is measured in hours to days, not seconds.

### 4. Generic AI "fill this template" tools
- Several exist that will draft a commercial invoice from a prompt.
- None of them (a) classify the HS code with duty-rate awareness, (b)
  know which additional documents are required for a specific destination
  country + product category, or (c) cross-validate the full package for
  internal consistency and destination-specific compliance gaps.
- This is the exact gap: generation without validation is not a usable
  product for something with real financial and legal consequences.

## What FreightDoc uniquely does
1. Classifies HS code with a defensible confidence score, not a guess.
2. Encodes destination-country-specific document *requirements* as a rule
   engine (not left to the LLM to "remember" — this is looked up, not
   hallucinated).
3. Generates the full multi-document package in one structured pass.
4. **Cross-validates the generated package** — checking HS code consistency,
   value/quantity mismatches between invoice and packing list, missing
   required fields, and destination-specific compliance gaps — and reports
   a compliance score plus a ready-to-ship boolean.
5. Does all of this in under 90 seconds for a fraction of the cost of a
   forwarder or enterprise software license.
