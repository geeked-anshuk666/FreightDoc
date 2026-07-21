# Deterministic-first and optional-AI safety contract

FreightDoc is a documentation-preparation workspace, not a customs broker,
sanctions-screening provider, carrier, filing system, or legal adviser. The
deterministic workflow must remain usable with no AI key, AI provider, network
connection, or AI response. AI is an optional, out-of-band assistant.

## What is authoritative in the workspace

Only a user-authorized, versioned workflow action may create or change a
canonical trade fact, document revision, rule/playbook publication, review
decision, or export. Deterministic rules, approved templates, explicitly saved
assumptions, local reference data, and human entry/review are the baseline.

AI may produce a *suggestion*, never an authoritative result. A suggestion is
reviewable before use and must not automatically overwrite a fact, generate a
final revision, approve a dossier, select an HS classification, publish a
rule, clear a screening result, transmit data, or submit a filing.

## Suggestion provenance and review

Where an AI feature is enabled, retain the minimum review record needed to
explain it: provider and model identifier, prompt/template version, timestamp,
bounded input artifact or fact identifiers, output schema/version, confidence,
rationale, and evidence/source identifiers. Do not retain raw uploads, access
tokens, full prompts containing unnecessary trade data, or provider secrets.

The UI/API must make the source and suggestion status visible. A user must be
able to accept, reject, or manually override each proposed field or revision.
The resulting immutable revision/audit event records the actor, decision,
timestamp, accepted or waived finding(s), and required reason. Maker/checker
separation, when enabled, prevents the maker from approving their own task.
An approval records an internal workflow decision only; it is not broker,
customs, legal, sanctions, or carrier approval.

## Safe unavailable-provider behaviour

AI failure is non-blocking. Missing configuration, timeout, refusal, malformed
output, low confidence, or provider outage must leave the deterministic result
and manual path available. Return a bounded, redacted status such as
`unavailable`, `failed`, or `needs_manual_review`, plus a retryable task when
appropriate. Never replace an unknown value with a plausible value or present
an unavailable provider as a successful check.

AI calls are optional feature-flagged enhancements. The feature flag controls
whether a suggestion request may be attempted; it does not gate manual entry,
native extraction, local rules, template generation from approved facts,
quality checks, review, or dossier export. New flags default off until their
privacy review, tests, observability, and rollback owner are recorded.

## Privacy boundary

Original upload bytes are transient: do not persist them in database records,
logs, prompt histories, exports, public links, or PWA caches. Keep only
permitted bounded metadata, hashes, extracted/reviewed facts, provenance, and
rendered/reviewed artifacts under the retention policy. Generic logs and
operational metrics must redact fact values, party names, document text,
credentials, and tokens. Scope all reads, actions, audit access, exports, and
sharing to the owning organization/owner.

## Regulated and paid integrations: honest status language

Until an approved adapter is connected and its prerequisites are satisfied,
use explicit boundary statuses:

| Area | Required status when disconnected | Never claim |
|---|---|---|
| Restricted-party screening | `not screened` / `manual review required` | cleared, sanctioned-party-free, or authoritative screening |
| Customs/clearance | `not connected` / `not filed` | filed, accepted, cleared, or customs-approved |
| Carrier/EDI | `not configured` / `requires approved vendor` | live tracking, transmitted, or certified EDI |
| SSO/SCIM | `not configured` / `requires enterprise approval` | provisioned, domain-verified, or SCIM-managed |

Activation requires the applicable vendor/customer agreement, credentials,
security review, scope controls, audit trail, and—where relevant—licensed or
official data, broker/customs authorization, certification, and liability
approval. A mock/local/CSV adapter is not a live regulated integration.

## Export and presentation language

Every relevant screen and export retains the informational-preparation and
licensed-broker-review disclaimer. `review_ready` or `ready_to_ship` means
internally review-ready only; it never means legally compliant, screened,
filed, cleared, accepted by a carrier, or approved by an authority.
