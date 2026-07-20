# Implementation notes

## Provider reality

The executable backend reads `AI_PROVIDER` and `AI_MODEL` from the environment
and currently defaults to Groq with `llama-3.3-70b-versatile`. Earlier planning
documents specify different models; they are preserved as hackathon source
requirements, not evidence of the currently deployed provider. Change the
runtime provider only with matching client implementation, tests, changelog,
and prompt/schema review.

## Structured AI boundary

`services/groq_client.py` maintains separate structured system instructions
for classification, document generation, and validation. It sends the
validated shipment facts through each relevant stage, validates model JSON with
Pydantic, and retries malformed output once. Free-form model prose never drives
tariff rates, rule selection, or PDF rendering.

## Provenance

`PipelineService` gathers tariff evidence concurrently where possible, resolves
the deterministic country rule set, and returns source/retrieval/fallback/rule
metadata with the legal-review disclaimer. Fallback evidence is visibly marked
and never presented as a confirmed current duty rate.

## Document intake

The intake service verifies file signature and limits before invoking PyMuPDF,
python-docx, openpyxl, or Pillow. It returns field suggestions with provenance
only; a user must review them before applying them to a shipment. Original bytes
are not written to a database or persistent file store.
