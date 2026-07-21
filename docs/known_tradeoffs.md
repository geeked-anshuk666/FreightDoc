# Known tradeoffs

FreightDoc is a reviewable preparation workflow, not customs filing, clearance, screening, or legal advice.

| Area | Current boundary |
|---|---|
| Corridors | US→DE/GB/IN/JP/CA/AU, IN→US, and CN→a specific EU member only. |
| Requirements | Local versioned rules are deterministic; users must verify current requirements with qualified experts. |
| Tariff/classification evidence | Provenance and fallback states are shown; neither is a binding ruling or live duty quote. |
| Runtime AI | Optional, Groq-oriented configuration; unavailable AI falls back to deterministic/manual handling. It is separate from Codex/ChatGPT development-tool disclosure. |
| Integrations | Connector, screening, and clearance interfaces are manual/mock/local unless an approved live provider is configured. No state may claim filed, cleared, accepted, certified, or screened merely from a mock/local result. |
| Documents | Intake is bounded and transient; extraction is a suggestion requiring review. |
| Infrastructure | Render, Vercel, and Neon free tiers can cold-start or impose quotas; they provide no production SLA. |

A generated dossier does not guarantee acceptance by a carrier, importer, customs authority, or regulator. Review this document when rules, sources, integrations, or retention policy change.
