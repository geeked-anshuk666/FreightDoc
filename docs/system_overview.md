# System overview

FreightDoc turns a shipment brief into a reviewable export-documentation
dossier. A user supplies the product, valid country corridor, quantity, value,
currency, and commercial party names. The system then:

1. classifies the product into an HS-code suggestion with confidence;
2. retrieves tariff/commercial evidence from the appropriate deterministic
   source adapters, labelling any fallback;
3. resolves required documents from versioned `country_rules.json` rather than
   asking a model to remember law;
4. generates structured document data;
5. cross-validates quantities, values, missing documents, and destination
   requirements; and
6. renders downloadable PDFs.

The app separates determinate work (rules, source retrieval, PDF rendering)
from AI work (classification, document filling, cross-validation). Every
result includes a request ID, source/rules provenance, and a broker-review
disclaimer. UN Comtrade is trade context, not a live duty decision.

The public product pages are crawlable; the Clerk-authenticated workspace is
private/noindex. Saved workspaces use the verified Clerk subject as an owner
scope and retain no Clerk profile data or original upload bytes.
