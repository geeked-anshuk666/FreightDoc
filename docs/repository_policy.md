# Repository policy

FreightDoc keeps the published repository reproducible while keeping personal,
machine-local, and sensitive material out of Git history.

## Two ignore layers

| Layer | Purpose | Examples |
|---|---|---|
| Committed `.gitignore` | Material that is unsafe or useless for **every** clone | environment files, virtual environments, Python cache, coverage, private documentation |
| Local `.git/info/exclude` | A developer's machine-only material; never pushed | personal screenshots, downloaded video, local task plans, IDE state, test recordings, local build artefacts |

Use `.git/info/exclude` for requests such as "ignore my local documents" or
"ignore this machine's recordings." Do not add broad personal paths to the
published `.gitignore`, and do not use a tracked ignore file as a substitute
for deleting a credential that was already committed.

### Recommended local exclusions

After cloning, add the following kinds of paths to `.git/info/exclude` when
they exist locally:

```text
.private_docs/
.env
backend/.env
frontend/.env.local
backend/venv/
frontend/node_modules/
frontend/dist/
outputs/
chrome-check/
screenshots/
downloads/
recordings/
*.sql
*.dump
```

Use repository-relative paths only. Never put a drive root, home directory, or
wildcard that could hide production source changes.

## Secrets and sensitive data

- Secrets are injected through Render, Vercel, Clerk, Neon, or a developer's
  local environment. Source code refers to variable names, never values.
- Treat exposed credentials as compromised: rotate them first, then remove
  them from history before sharing the repository.
- Never commit original uploaded trade documents, extracted passport/identity
  data, database dumps, auth headers, session tokens, or browser profiles.
- `VITE_CLERK_PUBLISHABLE_KEY` is client-visible by design, but server secrets
  such as AI keys and database URLs must never use the `VITE_` prefix.

The CI hygiene job catches tracked environment files and a narrow set of
common high-risk token prefixes. It is a backstop, not permission to skip
human review or a dedicated secret scanner in a larger organization.

## Logical history reconstruction

The initial Git history is a dependency-ordered reconstruction of the current
working tree; it must not pretend to have earlier timestamps, authors, or
events. Use explicit path staging and inspect every staged diff:

```powershell
git diff --cached --check
git diff --cached --stat
git status --short
```

Do not begin a baseline with `git add .`. A good FreightDoc commit describes
one user-visible or operational milestone and includes the relevant test and
documentation changes.

## Pull-request quality gate

Before merging or deploying, confirm:

1. No secret, private document, original upload, or generated output is
   staged.
2. Backend tests and frontend production build pass.
3. API/schema/security/deployment changes include matching documentation.
4. Public marketing pages may be indexed; authenticated shipment, dossier,
   upload, and download paths must remain private and `noindex`.
5. The change preserves FreightDoc's customs-broker review disclaimer and
   never presents a fallback or generated output as a filing guarantee.
