# FreightDoc Review-Ready MVP

**Status:** approved hackathon implementation slice
**Last updated:** 2026-07-20
**Scope:** one signed-in exporter prepares, reviews, and downloads one shipment dossier. FreightDoc remains an informational preparation tool; it never files customs entries or grants legal approval.

## Product promise

Turn a shipment brief and supporting paperwork into a **review-ready dossier**: the exporter can see what was supplied, what is missing, which evidence was used, and which issues require human attention before handoff to a customs broker.

## Exact in-scope journey

1. A signed-in user lands on **My shipments** and sees their own recent work only.
2. They create a draft or reopen one, with a visible lifecycle state and last-updated time.
3. They enter/review core facts: product, detailed description, origin, destination, quantity, declared value, currency, exporter, and importer. Optional UI-only fields must not be represented as pipeline facts until the API supports them.
4. They upload a supported source document. FreightDoc validates and extracts it in memory, persists only metadata/extracted suggestions, and discards the original bytes.
5. Extraction results show field, proposed value, confidence, provenance, and errors. A user must explicitly apply a suggestion; extraction never overwrites a shipment fact.
6. The user submits the complete draft for review and runs dossier preparation.
7. FreightDoc presents readable requirements, generated-document cards, tariff/rule provenance, readiness score, and actionable validation findings. Raw API JSON is never a production UI.
8. The user downloads a user-scoped complete PDF dossier. The download response is private/no-store and includes the legal-review disclaimer in the product result.

## Lifecycle semantics

The implementation may use a small set of persisted status labels, but their user-facing meaning is fixed:

| User-facing state | Meaning | Allowed next action |
|---|---|---|
| Draft | Core facts are incomplete or still being edited. | Save, edit, upload evidence, delete. |
| Preparing | The dossier pipeline is running. | Wait/retry after a recoverable error; prevent duplicate submission. |
| Needs review | Pipeline completed with missing required data, low confidence, fallback evidence, or critical findings. | Fix facts, re-upload/review evidence, then run preparation again. |
| Review-ready | No critical blocker remains, but this is still informational and needs broker/legal review when indicated. | Download dossier or continue review. |

The persisted lifecycle is `draft` → `processing` → (`needs_review` or `review_ready`) and may end as `archived`. A successful preparation also creates a dossier record; it must be presented as a generated result, not a separate legal approval state. Do not imply a formal approval workflow until roles, assignments, and decision logging are implemented.

## Human-review safety rules

- A readiness score is a prioritization signal, never a clearance, filing, or legal conclusion.
- Critical validation findings, low classification confidence, missing required documents, and tariff fallback evidence must be visually distinct and must explain the next action.
- A generated dossier must display source/retrieval provenance, rules version/date, model/provider information where returned, and the broker-review disclaimer.
- Uploaded-document suggestions require an explicit apply action. The UI must identify them as suggestions and retain their source/confidence.
- The default retention policy discards original upload bytes after processing. Retry therefore requires a re-upload; the product must say this clearly.
- Users can access only their own saved shipments, documents, dossiers, parties, and downloads. Clerk authentication provides identity; the application stores the opaque Clerk subject as the ownership key, not passwords or copied profile data.

## Deliberately deferred from this MVP

- Organizations, roles, invitations, reviewer assignment, comments, and broker portals.
- Formal approve/reject/waive decisions and immutable version comparison.
- Product/party library reuse beyond the existing owner-scoped party search.
- Background jobs, notifications, share links, payments, carrier booking/tracking, filing integrations, and persistent input-file archive.

These are roadmap items, not hidden claims. See `saas_product_roadmap.md` and `../docs/what_we_skipped_and_why.md`.

## Judge demo script (75–90 seconds)

1. Sign in and open **My shipments**; point out ownership-scoped drafts and their lifecycle status.
2. Open a sample draft and show the guided trade-route/cargo/commercial workflow.
3. Upload a packing list or invoice fixture. Explain that the file is processed, suggestions are reviewable, and the original is not retained.
4. Show a suggestion with confidence/provenance and explicitly apply or reject it.
5. Prepare the dossier. Narrate the deterministic requirements/tariff lookup, structured generation, and cross-validation boundary.
6. On the dossier, show readiness, a critical/warning example, the required-document cards, and the broker-review disclaimer.
7. Download the complete PDF and finish with: “FreightDoc makes documentation review-ready before cargo moves; it does not replace a broker.”

## Acceptance checklist

### Functional

- [ ] A signed-in user can create, save, reopen, update, and delete only their shipment drafts.
- [ ] The dashboard displays a useful empty state, recent shipments, lifecycle label, route, and a clear continue/new action.
- [ ] Core fact completeness is checked before review/dossier generation, with field-specific guidance.
- [ ] Document upload rejects unsupported, unsafe, oversized, and over-aggregate uploads with readable errors.
- [ ] Each saved extraction result shows type, status, confidence, provenance, fields, and retry/remove action.
- [ ] The user can explicitly apply an extracted suggestion; it never silently changes the draft.
- [ ] The preparation result uses UI components for documents, requirements, findings, provenance, readiness, and actions—never `JSON.stringify`, `<pre>`, or raw object dumps.
- [ ] Complete-dossier download has loading, success, and error states and calls the authenticated PDF endpoint.

### Trust and quality

- [ ] Low confidence, fallback tariff evidence, missing required documents, and critical findings are prominent and understandable.
- [ ] Every dossier result includes correlation ID, rules/source provenance, and the legal-review disclaimer.
- [ ] Original input bytes are not stored; retry messaging asks for a re-upload.
- [ ] Desktop, tablet, and mobile layouts have no horizontal overflow; keyboard navigation, focus visibility, and reduced-motion fallback work.
- [ ] Authenticated responses and dossier downloads are not put into the PWA cache.

## Required implementation tests

Do not mark these as passed until automated or manually recorded against the deployed build.

| Area | Required case |
|---|---|
| Ownership | User A cannot list, read, patch, upload to, download from, or delete User B’s shipment by changing an ID. |
| Lifecycle | Incomplete draft cannot be submitted; complete draft can enter review; a completed dossier maps to the right user-facing state. |
| Extraction | Supported document succeeds; spoofed MIME, unsafe archive, oversized file, and parser timeout return safe errors; original bytes are not persisted. |
| Suggestions | Extracted values are displayed with source/confidence; apply is explicit; reject/no-op leaves user-entered values unchanged. |
| Pipeline | Tariff timeout is labelled as fallback; malformed AI output retries once then returns a safe error; low confidence and critical findings produce Needs attention. |
| Dossier | Requirements and generated docs render as cards, a readiness score is responsive, and complete/document PDF downloads use authenticated user scope. |
| UX | Dashboard empty/loading/error states, mobile form flow, upload states, keyboard controls, and no-raw-JSON regression are covered. |
