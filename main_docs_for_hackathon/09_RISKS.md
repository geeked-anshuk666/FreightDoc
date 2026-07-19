# FreightDoc — 09_RISKS.md

## Risk 1: Getting an HS code wrong has real legal/financial consequences
**Mitigation:** Always surface the confidence score to the user. Below a
threshold, flag "low confidence — recommend human customs broker review"
rather than silently presenting a guess as fact. Disclaim clearly:
informational tool, not a substitute for a licensed customs broker.

## Risk 2: Tariff/compliance rules change frequently
**Mitigation:** Keep the country-rules JSON as a versioned, easily-updatable
config file separate from code. For the hackathon, freeze the 8 launch
corridors' rules as of a known date and state that date in the UI.

## Risk 3: Public APIs (USITC, UN Comtrade) can be flaky or rate-limited
**Mitigation:** Cache successful lookups locally (dict or Redis). Have a
hardcoded fallback tariff dataset for the 8 launch corridors so the demo
never breaks live on judge day regardless of API uptime.

## Risk 4: Cross-validator hallucinating an error that isn't real (or missing
a real one)
**Mitigation:** Frame all cross-validator output as flags for human review,
never as an automatic block on shipping (except the most severe, obviously
structural ones like a raw value mismatch between two documents, which is a
deterministic string/number comparison you can also do in code as a
double-check independent of the LLM).

## Risk 5: PDF generation breaking under time pressure
**Mitigation:** Fallback path — render documents as styled HTML and let the
browser's native print-to-PDF handle rendering. Functionally equivalent for
demo purposes.

## Risk 6: Running low on credits mid-build
**Mitigation:** Not expected to occur (2,500 credits vs. ~500 credits
estimated total usage), but if it does: switch all Codex building to Terra
exclusively, restrict Luna calls to only the full-pipeline endpoint during
testing, and stop calling `/api/classify` or `/api/validate` standalone
during development.
