# FreightDoc — technical architecture

React/Vite/PWA with Clerk provides the workspace. FastAPI, SQLAlchemy, versioned local rules, and ReportLab provide the API, records, deterministic requirements, and PDFs. Postgres/Neon persistence is enabled when configured; Render and Vercel configuration are included.

The pipeline is: shipment facts → deterministic corridor/rule resolution and labelled evidence → draft documents and validation → human review/revisions → PDF dossier. Optional runtime suggestions use the executable `AI_PROVIDER`/`AI_MODEL` configuration (currently Groq-oriented) and are not authoritative. Canonical record, quality, operations, and connector interfaces are documented in the [system overview](../docs/system_overview.md) and [API reference](../docs/api_reference.md).

Codex/GPT-5.6 development-tool claims belong in the evidence-gated [AI usage disclosure](../docs/ai_usage_disclosure.md), not runtime architecture.
