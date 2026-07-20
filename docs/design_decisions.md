# Design decisions

## Deterministic rules before AI

Country/document requirements are version-controlled JSON rather than LLM
memory. This keeps corridor/category decisions reviewable, testable, dated,
and traceable to source URLs. Tariff retrieval and PDF rendering follow the
same deterministic boundary.

## Separate AI stages

Classification, structured document generation, and cross-validation are
separate calls. The separation allows a malformed response to be retried once,
keeps template filling cheaper than classification, and lets the validator
challenge the generated package rather than repeat the same prompt context.
The executable provider/model is configuration-driven; product copy must never
claim a provider/model that is not actually configured.

## Owner scope without identity profiling

Clerk handles sign-in. FreightDoc persists only the verified opaque Clerk
subject when a workspace is saved. Emails, names, OAuth data, raw JWTs, and
session tokens provide no value to dossier generation and are intentionally not
stored.

## Editorial single workspace

The Shipment Desk is one editable workflow rather than a hard wizard. Its
responsive rail/stepper explains the preparation sequence while allowing a
busy exporter to correct route, cargo, commercial, party, and document facts
without losing context. Optional fields are labelled when the current backend
does not submit them, preventing false data capture.
