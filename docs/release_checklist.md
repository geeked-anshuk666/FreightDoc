# Release checklist

Use this against the exact submitted commit. Record an owner, timestamp, and redacted result for each item.

- [ ] `git status --short` is understood; `git diff --check` passes; tracked files contain no private docs, uploads, or `.env` files other than approved examples.
- [ ] Review `git check-ignore -v` for a sample env file, dependency directory, build directory, cache, output, and `.private_docs/`; confirm templates/configuration remain visible.
- [ ] Check README and canonical-doc relative links; do not guess external deployment URLs.
- [ ] Run backend: `cd backend; python -m pytest tests -q`.
- [ ] Run frontend: `cd frontend; npm ci; npm run test; npm run build`.
- [ ] Verify `/health`, exact CORS origins, unauthenticated protected-route rejection, deterministic operation without an AI key, fallback labels, a PDF export, and owner deletion.
- [ ] Run controlled database migration before code that needs it; an app rollback does not undo a migration.
- [ ] Verify Render/Vercel/Neon/Clerk dashboard configuration and acknowledge free-tier cold starts/quotas.
- [ ] Confirm synthetic demo data only; rehearse and upload the voiceover video as public or unlisted.
- [ ] Capture Codex `/feedback` session ID; verify Codex/GPT-5.6 wording and any effort claim against local evidence.
- [ ] If private, share repository access with `testing@devpost.com` and `build-week-event@openai.com`.
- [ ] Confirm Devpost reads **Submitted**, not Draft, before the event deadline; make no changes after the deadline.
