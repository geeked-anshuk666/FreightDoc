# Known tradeoffs

FreightDoc is an export-documentation preparation tool. It is not a customs
broker, tariff ruling service, broker-of-record, or filing guarantee. The
following boundaries are intentional and visible in the product rather than
hidden behind automation.

| Area | Current decision | Why it is reasonable now | What changes before broad production use |
|---|---|---|---|
| Legal/compliance | Informational dossier with a broker-review disclaimer | The product's value is internal consistency and preparedness, not legal authority | formal legal review, official-source refresh process, jurisdiction-specific product governance |
| Corridors | Eight supported corridors; China exports require a specific EU member-state destination | keeps country rules testable and explicit | expand rules only with an owner, source citation, effective date, and regression fixtures |
| Tariff evidence | USITC/TARIC evidence where applicable; UN Comtrade is context, not live duty determination; fallbacks are labelled | public sources can be slow/unavailable | paid/official data agreements, source monitoring, tariff-line-specific review workflow |
| AI | Provider/model are runtime configuration, not a hard-coded marketing promise | legacy documents conflict with executable Groq configuration | pin and test approved model versions, establish eval gates and provider failover |
| Pipeline latency | initial flow can be synchronous | makes the demo easy to understand | idempotent queued jobs, status notifications, concurrency controls |
| Upload security | strict size/type/resource sanitation and temporary processing | protects a free-tier service without persisting originals | managed malware scanning, isolated worker sandbox, independent security review |
| OCR | bounded OCR/extraction only when a genuine worker is available | avoids fabricating data from a scan | provision OCR worker capacity and quality evaluation for trade-document layouts |
| Original files | discard after processing; retain only approved metadata/extracted facts when persistence is enabled | minimises sensitive data retention | explicit opt-in encrypted retention with purpose, expiry, access log, and deletion controls |
| Identity | store only opaque Clerk `sub`/owner ID for owner-scoped data | avoids unnecessary profile/OAuth/token collection | conduct privacy review before syncing user name, email, organisations, or roles |
| Database | Neon Postgres is used only when owner-scoped persistence is active | managed serverless Postgres suits a free-tier demo | backup/restore drills, migration release discipline, capacity planning and regional strategy |
| Availability | Render/Vercel/Neon free tiers | zero-cost demo deployment | paid capacity, SLOs, multi-region recovery, on-call ownership |
| PWA | cache public versioned assets only | offline shell is useful; private data must not linger in a browser cache | authenticated offline data only with an explicit encrypted/offline-data threat model |
| Accessibility | semantic controls, keyboard support, focus states, and reduced-motion fallbacks are required | improves basic usability now | continuous accessibility audits with assistive technology and localisation testing |

## Explicit non-guarantees

- A high readiness score is not customs clearance or legal approval.
- A generated PDF is not proof that an importer, carrier, customs authority,
  or regulator will accept it.
- A fallback tariff rate is not a live rate.
- Document extraction is a suggestion and must be reviewed before it changes
  shipment facts.
- Free-tier infrastructure does not provide an uptime, recovery-time, or
  security-service-level agreement.

Review this document whenever a route, external source, model, persistence
policy, or document-retention rule changes.
