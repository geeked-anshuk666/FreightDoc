# What we skipped and why

This document records what FreightDoc deliberately does **not** do. A missing
feature is not silently treated as complete merely because the interface looks
polished.

| Not included | Why it is out of scope | Prerequisite to add it safely |
|---|---|---|
| Customs filing or broker-of-record service | requires licensed jurisdiction-specific responsibility and workflows | broker partnerships, legal controls, filing authority, liability model, audit trail |
| Guaranteed tariff/legal ruling | public APIs and generated classification do not replace an official ruling | authoritative data agreements, legal review, decision provenance and appeal workflow |
| Every country/product regime | rules need maintained source references and regression tests | named rule owner, source/effective-date lifecycle, coverage evaluation |
| Billing and subscription management | distracts from correct documentation preparation | product usage model, tax/payment compliance, support and entitlement layer |
| Persistent original-file archive | increases sensitive-data and breach exposure | explicit user retention choice, encrypted object store, access audit, expiry/deletion process |
| Resident antivirus on Render Free | free web services are not dependable malware-scanning infrastructure | managed scanning service or isolated scanner workers with fail-closed policy |
| Always-on OCR farm | image/PDF OCR is CPU-heavy and unsuitable for a small synchronous free service | bounded worker queue, capacity budget, layout quality evaluation, failure recovery |
| Real-time carrier booking/tracking | it is a separate operational domain from dossier preparation | carrier contracts, webhook ingestion, SLA/identity model, customer support |
| Multi-user organisation permissions | Clerk sign-in alone is not a complete B2B authorisation model | organisation schema, roles, invitations, audit permissions, data-sharing policy |
| Offline access to private dossiers | caching private trade data changes the threat model | encrypted local storage, session expiry handling, device-loss controls, user consent |
| Native mobile applications | the responsive PWA is the initial mobile surface | user research, mobile threat model, store release/maintenance capacity |

## Why this matters

FreightDoc is strongest when it tells the user what it knows, the source and
time of that evidence, and where human review is required. Adding a feature
without its operational, security, and legal support would make the product
look more complete while making it less trustworthy.

For the implemented path and its operational limits, read
[known tradeoffs](known_tradeoffs.md). For a staged expansion plan, read
[scaling](scaling_to_1_billion_users.md).
