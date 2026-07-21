# FreightDoc documentation, repository, and demo release plan

## Status and scope

**Status:** proposed; no product code, deployment configuration, or existing
file is changed by this plan.  The release work is documentation and repository
hygiene only, except for a replacement of the root `.gitignore` after review.

**Release objective:** make the public repository understandable, runnable,
honest about its product and AI boundaries, safe to publish, and ready for a
minimal one-take hackathon demo.

### Evidence inventory

The public documentation is already substantial, but it is distributed across
three audiences:

| Location | Current role | Release disposition |
|---|---|---|
| Root `README.md`, `CHANGELOG.md` | public entry point and release notes | retain and make the README canonical |
| `docs/` | product, API, architecture, security, testing, deployment and operating documentation | retain; consolidate links and correct stale claims |
| `main_docs_for_hackathon/` | pitch, demo, risk, architecture and hackathon-facing material | retain until the submission package has been reviewed |
| `meta_docs/` | prior product/planning/reference material | retain as internal planning history; do not present as runtime truth |
| `.private_docs/` | private interview/design rationale | retain locally and ignore; verify it is not tracked before public push |
| Root planning notes (`freightdoc-*.md`, `cargo-story-rebuild.md`, `auth-help-text-contrast.md`) | implementation history and point-in-time work notes | review individually; do not delete solely because a newer plan exists |

Current executable and deployment evidence supports these public claims:

- React/Vite PWA frontend with Clerk; FastAPI/Pydantic backend with SQLAlchemy,
  ReportLab, and a Postgres/Neon persistence path.
- Render backend (`render.yaml`, `backend/Dockerfile`) and Vercel frontend
  (`frontend/vercel.json`) deployment configuration.
- A deterministic documentation workflow that can work without an AI key;
  the configured AI integration is optional and currently Groq-oriented.
- Reviewable facts, revisions, validation/quality findings, PDFs, local rules
  and playbooks, and mock/manual integration boundaries.
- The public safety contract explicitly says the product is informational
  preparation software—not a broker, filing, clearance, screening, or legal
  service—and requires human review for consequential outcomes.

### Authoritative Build Week submission constraints

The supplied Build Week materials include generic/reference material that is
not FreightDoc-specific; none of those examples may be reused as FreightDoc
product, model, effort, capability, or metric evidence.  The following
user-provided Devpost/OpenAI Build Week checklist is authoritative for this
release plan:

- Submit by **Tuesday, July 21, 5:00 PM PT**; use an early-upload buffer.
  After the deadline, make no changes.
- The project must use both **Codex** and **GPT-5.6**; API credits are not a
  prerequisite.
- The YouTube video may be public or unlisted, requires voiceover, and must
  explain what was built and how both Codex and GPT-5.6 were used. Judges may
  stop watching at three minutes.
- Retrieve the Codex `/feedback` Session ID and include it in the submission.
- The README needs setup instructions, sample data where needed, and
  documentation of Codex/GPT-5.6 use throughout.
- A private repository must be shared with `testing@devpost.com` and
  `build-week-event@openai.com`.
- Confirm team invitations and confirm the Devpost entry is **Submitted**, not
  Draft.

Treat the deadline date/time as an event constraint supplied by the user; the
release owner must confirm the event timezone in Devpost immediately before
submission.  The previously expected root `context.txt` is still absent from
the FreightDoc tree, but its absence no longer blocks this plan because the
authoritative checklist above supersedes it for release gating.  It remains a
review item if later restored.

## Documentation information architecture

The public README should be the short, code-accurate front door.  `docs/`
should hold durable operational detail.  Hackathon material should stay in a
clearly labelled submission package rather than competing with the README.
Historical planning material must be labelled historical so it cannot be read
as a feature claim.

### Exact file actions

| Action | File | Required outcome |
|---|---|---|
| Update | `README.md` | Replace with the canonical public README described below. Link only to maintained public docs. |
| Update | `.gitignore` | Replace the narrow current rules with the production policy below; preserve `backend/.env.example`. |
| Update | `docs/repository_policy.md` | Define public/private document classes, allowed fixtures, secrets procedure, and the no-delete-without-review rule. |
| Update | `docs/deployment_guide.md` | Reconcile every variable name, platform setting, migration instruction, health check, and rollback statement with current config. State that provider keys are optional for the deterministic workflow. |
| Update | `docs/testing_strategy.md` | Reconcile test counts only by running the suite at release time; retain deterministic/no-live-provider test policy and add the release verification commands. |
| Update | `docs/system_overview.md` | Make the canonical feature and boundary summary match implemented routes/UI only; cross-link the safety contract. |
| Update | `docs/api_reference.md` | Regenerate/reconcile from FastAPI route schemas and mark mock/manual connector endpoints accurately. |
| Update | `docs/known_tradeoffs.md` | Record unsupported corridors, fallback/source limitations, manual review requirements, free-tier limits, and non-live integration status. |
| Update | `main_docs_for_hackathon/05_DEMO_SCRIPT.md` | Replace with the timestamped one-take script requirements below once `context.txt` is available. |
| Update | `main_docs_for_hackathon/00_MASTER.md` and `07_HACKATHON_FIT.md` | Add the authoritative Build Week checklist, a dated source note, the `/feedback` Session ID placeholder, and only verified project-specific evidence. |
| Create | `docs/demo_video_runbook.md` | Presenter checklist, seed-data policy, browser/window setup, recovery cues, disclosure evidence, and the final approved script. |
| Create | `docs/documentation_index.md` | One-page audience map: public README, operator docs, architecture docs, hackathon submission docs, and private/non-public materials. |
| Create | `docs/release_checklist.md` | A repeatable pre-push/pre-deploy checklist containing repository, documentation, test, build, link, and deployment checks below. |
| Create | `docs/ai_usage_disclosure.md` | Evidence-backed disclosure of development assistance. It must distinguish development tools from runtime product AI and include only verified model/effort claims. |

Do not create duplicate API, architecture, testing, or demo documents outside
these destinations.  Where existing documents overlap, `documentation_index.md`
will name the canonical one and the duplicate will be either reduced to a
short historical note or proposed for archival review—not silently deleted.

## Canonical README specification

The README should be 1–2 screens before its detailed links and use this order:

1. **Name, one-sentence value proposition, and safety boundary.** Say that
   FreightDoc prepares a reviewable export-documentation dossier; explicitly
   say it is not a broker, legal adviser, screening authority, carrier, or
   filing/clearance service.
2. **What is built today.** A concise feature list sourced from routes and UI:
   deterministic document/rule workflow, classification and tariff evidence
   with provenance/fallback labels, reviewable facts/revisions, validation,
   PDF dossier output, document intake with transient originals, and
   local/mock/manual connector surfaces only where implemented.
3. **How it works.** A small numbered flow: create shipment → add/review facts
   and source documents → generate/validate a draft → resolve findings with a
   human reviewer → export a dossier.  Do not equate this with filing or
   clearance.
4. **Supported corridors and limitations.** Cite the exact current route list
   from code/data, including the requirement for a specific EU country in the
   China-to-EU case.  Link to `docs/known_tradeoffs.md`.
5. **Architecture and stack.** React/Vite/PWA + Clerk; FastAPI + SQLAlchemy;
   Neon/Postgres when persistence is configured; Render/Vercel deployment.
   Avoid calling every planned module a live service.
6. **AI and data handling.** Explain deterministic-first behavior, optional
   suggestion-only AI, failure fallback, human acceptance, provenance, and
   transient upload bytes. Link to `docs/deterministic_ai_safety_contract.md`.
7. **Local setup.** Verified PowerShell commands, Python/Node prerequisites,
   exact environment variable *names*, and a statement never to commit values.
   Preserve the tested backend and frontend commands rather than inventing a
   single monorepo command.
8. **Tests and deployment.** Verified commands, CI behaviour, Render/Vercel/
   Neon setup links, health endpoint, and explicit free-tier/cold-start caveat.
9. **Documentation and contribution/security contact.** Link to the canonical
   index, deployment/testing/security docs, changelog, license if one exists,
   and a responsible-disclosure path only if an owner/contact is supplied.
10. **Hackathon and development-tool disclosure.** State that Codex and
    GPT-5.6 were used only after the factual evidence checklist passes; link
    to the submission disclosure and provide the required `/feedback` Session
    ID only where the submission form requires it. Never expose credentials,
    raw prompts containing private data, or other session content.

The README must additionally include synthetic/sample shipment data (or a
safe reproducible seed procedure) sufficient for a reviewer to exercise the
document workflow without customer records, credentials, or an AI key.

The author must validate every version/provider/test-count claim against the
release revision.  In particular, do not repeat legacy planning references to
different runtime models, claim a live regulatory integration, or promise
customs compliance/clearance.

## Production `.gitignore` policy

Replace the current minimal ignore list with comments and categories covering:

```gitignore
# Secrets and local configuration (keep committed templates only)
.env
.env.*
!.env.example
!.env.*.example
*.pem
*.key
*.p12
*.pfx

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
coverage.xml
htmlcov/
.venv/
venv/
env/

# Node/Vite
node_modules/
dist/
coverage/
.vite/
*.tsbuildinfo

# Test, build, and runtime artifacts
.mypy_cache/
.ruff_cache/
.hypothesis/
.tox/
*.log
*.sqlite3
*.db

# Private/local material and generated demonstration artifacts
.private_docs/
outputs/
chrome-check/
*.mp4
*.webm

# Editor and OS metadata
.DS_Store
Thumbs.db
.idea/
.vscode/
```

Before applying it, compare candidate patterns against `git ls-files` and
explicitly preserve source, lockfiles, `render.yaml`, Dockerfiles, Vercel
config, migrations, public assets, test fixtures that are safe/synthetic,
`.github/`, and `backend/.env.example`.  An ignore rule never removes an
already tracked secret or generated file; those require a separate reviewed
remediation commit and, for exposed credentials, immediate rotation.

## Cleanup candidate register

No deletion is authorized by this plan.  The implementation owner must produce
an exact `git ls-files`/size/last-reference report and obtain approval before
removing any item.

| Class | Candidate | Required handling |
|---|---|---|
| Safe to remove after confirming untracked | `frontend/node_modules/`, `frontend/dist/`, `.pytest_cache/`, Python `__pycache__/`, `.vite/`, coverage output | Regenerate from lockfile/source; first confirm they are untracked and not a demo dependency. |
| Safe to remove after confirming untracked and not needed as evidence | local `outputs/` render products, `chrome-check/` browser artifacts, local video recordings | Preserve a reviewed final demo artifact outside the repository if needed; do not remove user-owned assets blindly. |
| Review required | Root point-in-time notes: `auth-help-text-contrast.md`, `cargo-story-rebuild.md`, `freightdoc-login-pipeline-hero-fix.md`, `freightdoc-production-hardening.md`, `freightdoc-test-suite.md`, `freightdoc-world-class-platform-plan.md` | Decide whether each is active release evidence, historical design record, or redundant. Prefer moving approved history to a labelled archive over deletion. |
| Review required | `meta_docs/` and `main_docs_for_hackathon/` overlaps | Identify canonical documents and submission requirements after `context.txt` review. Private/internal wording may be unsuitable for GitHub even if technically useful. |
| Review required | `.private_docs/` | Retain locally; verify ignored and untracked. If it was ever tracked, remove from the index only in an approved cleanup and assess exposure. |
| Retain | `backend/`, `frontend/` source and public assets, `docs/`, `.github/`, Docker/Render/Vercel config, migrations, safe test fixtures, `CHANGELOG.md`, README, `backend/.env.example` | These are executable, deployment, safety, test, or public documentation assets. |

## Demo-video runbook requirements

Produce a 90–120 second one-take recording; this leaves margin beneath the
three-minute judge attention window. Upload it to YouTube as public or
unlisted, with required voiceover. It should be cinematic through clean
composition, natural voice, paced cursor movement, and deliberate screen
states—not through edits, cuts, fabricated success messages, hidden tabs, or
claims that cannot be reproduced.

| Timestamp | Screen state | Spoken words (draft; verify screen labels before recording) |
|---|---|---|
| 0:00–0:10 | FreightDoc landing/workspace in a clean browser profile; title and disclaimer visible | “FreightDoc turns a shipment brief into a reviewable export-documentation dossier—before a human reviewer makes the final call.” |
| 0:10–0:28 | Create/open a pre-seeded synthetic shipment; route and commodity facts visible | “I start with the shipment facts: origin, destination, product, and commercial details. The workflow keeps these facts reviewable rather than treating an AI answer as final.” |
| 0:28–0:48 | Requirements/classification/evidence view | “FreightDoc applies deterministic route rules and shows the evidence and any fallback status behind the classification and document requirements.” |
| 0:48–1:08 | Generated document/revision or quality view; show a finding and human action | “It drafts the required paperwork, validates the dossier, and makes gaps visible. A reviewer can accept, correct, or waive a finding with a recorded decision.” |
| 1:08–1:22 | PDF dossier/export view | “Once it is internally review-ready, the team can export a dossier with its supporting context. That is preparation—not customs filing, clearance, or legal advice.” |
| 1:22–1:35 | Closing product screen plus a concise disclosure card/text file | “The core workflow still works without an AI key. AI, when enabled, is suggestion-only; a person remains accountable for the result.” |
| 1:35–1:50 | Development-tool disclosure evidence, only if verified | “I used Codex for [verified implementation/review tasks] and GPT-5.6 for [verified tasks]. [Only state a model variant or effort level when the local record shows it.] Runtime product AI is configured separately and is optional.” |
| 1:50–2:00 | Return to the clean product/closing screen | “FreightDoc makes export-document preparation more reviewable, traceable, and practical for teams moving goods across borders.” |

Use clearly synthetic company names, products, parties, invoice values, and
documents.  Disable notification pop-ups; use a fresh browser profile; zoom
to readable text; keep the browser at one resolution; pre-warm the free-tier
backend; and rehearse once without recording.  If an API/AI call fails, show
the deterministic/manual path and narrate the honest state instead of retrying
off camera.

### Model and effort disclosure evidence checklist

The original request asks for explicit Codex and ChatGPT 5.6 model/effort
details.  Those are development-process claims, not product-runtime claims,
and must be separately proven.  Before inserting a statement into the script,
README, or submission:

1. Locate a durable, permitted **local usage/session record** for each claim:
   the relevant Codex session/`/feedback` record, a local export/metadata
   record, or an approved project decision log. Capture the `/feedback` Session
   ID before the session closes and place it in the Devpost submission, not in
   a public secret-bearing transcript.
2. Record the exact product name, displayed model identifier, displayed effort
   level (if any), date/time, and work assisted. Do not infer an effort level
   from output quality, a system label, or the existence of a session.
3. **Never fabricate a GPT-5.6 effort level.** If a local record does not
   display one, state only the verified tool/model name and verified work; omit
   the effort level entirely. Verify the record says **ChatGPT 5.6** exactly
   if that is to be stated; do not rewrite “GPT-5.6”, “Codex”, or another
   displayed identifier into that name.
4. Separate development assistance from the executable runtime provider/model.
   Current code/config documentation supports a Groq-oriented optional runtime
   integration, not an automatic claim about Codex or ChatGPT model use.
5. Remove any unverified model, effort, percentage-of-code, or autonomous-work
   claim. The safe fallback is: “Development-tool details are disclosed in the
   project submission record; runtime suggestions remain optional and human
   reviewed.”
6. Obtain presenter approval for the final wording and keep the evidence with
   the private submission materials, never in a committed secret-bearing log.

### Factual evidence checklist

Before finalizing README, Devpost text, or voiceover, the release owner must
complete this table against the exact submitted revision:

| Claim category | Required evidence | Prohibited shortcut |
|---|---|---|
| Current FreightDoc feature | implemented UI/API path, test, or current source/config | a roadmap, mockup, or another project's reference document |
| Runtime AI/provider behaviour | executable configuration plus safety contract | development-tool usage or a historical planning model |
| Codex use | local Codex session and `/feedback` Session ID | a generic Codex statement without a session record |
| GPT-5.6 use | local session/usage record naming GPT-5.6 and the assisted work | assuming the model because the event requires it |
| Model variant/effort | local record displaying that exact value | guessing `low`, `medium`, `high`, `xhigh`, `max`, or `ultra` |
| Tests/build counts | command output from the submitted commit | historical counts in an earlier document |
| Hackathon requirements | the authoritative checklist above and final Devpost form | unrelated supplied project examples or memory |
| Demo/sample data | a committed safe fixture or documented deterministic seed path | customer documents, secrets, or unrepeatable manual data |

## Release validation and deployment outcomes

Run these checks against the exact release commit, record redacted results in
`docs/release_checklist.md`, and fix failures before pushing publicly:

1. `git status --short`, `git diff --check`, and `git ls-files` review: no
   unintentional artifacts; no tracked `.env` except approved examples; no
   private documentation or uploads.
2. Secret hygiene: scan tracked files for common credential prefixes and
   high-risk extensions; inspect Git history separately if a key may ever have
   been committed; rotate, revoke, and remediate rather than merely ignoring.
3. Ignore verification: use `git check-ignore -v` on representative env,
   dependency, build, cache, output, and private-doc paths; confirm required
   config/templates are *not* ignored.
4. Markdown links: check relative links from the README and canonical docs,
   heading anchors, and external links. Fail broken internal links; flag stale
   deployment URLs rather than guessing replacements.
5. Documentation truth check: trace every feature, corridor, endpoint,
   environment variable, provider/model, test count, and deployment assertion
   to current source/config or a dated release result.
6. Backend quality: from `backend`, create/use a local virtual environment,
   install requirements, and run `python -m pytest tests -q`. Record the
   observed count, not the historical target.
7. Frontend quality: from `frontend`, run `npm ci`, `npm run test`, and
   `npm run build`. Record actual pass/fail/count/build output.
8. Deployment smoke: verify deployed `GET /health`; exact CORS origins;
   protected-route rejection without a valid Clerk token where enabled;
   deterministic operation without an AI key; source/fallback labelling; a
   renderable PDF; and a user-owned deletion path.
9. Deployment-document outcome: the updated guide must name a controlled
   database migration step, dashboard-only secrets, Render rollback limits,
   Vercel environment scopes, Clerk allow-list setup, and free-tier cold-start
   limitations.  No docs may imply that rollback reverses a database migration.

### Build Week release and submission checklist

Complete these in order; assign an owner and timestamp to each item in the
release checklist.

1. **Evidence freeze:** complete the factual evidence checklist, approve the
   Codex/GPT-5.6 wording, capture the Codex `/feedback` Session ID, and freeze
   the exact commit used for README, video, and Devpost claims.
2. **Repository readiness:** run the validation commands above; publish only
   safe source, configuration, synthetic sample data, and public docs. If the
   repository is private, share it with `testing@devpost.com` and
   `build-week-event@openai.com`, then verify both invitations are accepted or
   accessible as required by the platform.
3. **README readiness:** verify clean setup commands, required environment
   variable names, synthetic sample/seed steps, product boundaries, deployment
   notes, and the evidence-backed Codex/GPT-5.6 disclosure are present.
4. **Video readiness:** record the one-take voiceover; state what FreightDoc
   does, how Codex was used, and how GPT-5.6 was used; check that all claimed
   screens are visible and all details match evidence. Upload to YouTube as
   public or unlisted, play it back once, and retain the URL.
5. **Devpost readiness:** complete required fields, README/repository/video
   URLs, team details, and the `/feedback` Session ID. Verify all team
   invitations.
6. **Early submission:** submit before the Tuesday July 21, 5:00 PM PT
   deadline, using an early buffer for uploads, rendering, and invitations.
   Confirm the status reads **Submitted**, not Draft, and capture a screenshot
   or other permitted confirmation.
7. **Lock after submission:** make no code, documentation, video, repository,
   or Devpost changes after the deadline. If a pre-deadline correction is
   essential, repeat the evidence, README, video, and submission checks for
   the new exact revision.

## Completion criteria

This plan is complete when the public README and linked canonical docs pass
truth/link checks, the clean `.gitignore` is verified against tracked files,
the candidate cleanup list has explicit approval decisions, all stated
tests/builds have been run, the recorded demo script contains only verified
development-tool/model/effort disclosures, the `/feedback` Session ID has been
captured for Devpost, reviewer access/team invitations have been verified when
applicable, the YouTube video has been uploaded, and the Devpost entry is
confirmed **Submitted** before the deadline.
