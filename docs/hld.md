# Historical high-level design note

This note is retained as planning history and is not the canonical architecture description. For the implemented system, use the [system overview](system_overview.md), [API reference](api_reference.md), and [deployment guide](deployment_guide.md).

FreightDoc currently uses a React/Vite frontend, FastAPI backend, versioned local rules, ReportLab PDFs, and optional Groq-oriented runtime suggestions. The deterministic/manual workflow remains available without an AI key, and it does not provide filing, clearance, screening, or legal determinations.
