# Changelog

All meaningful FreightDoc changes are documented here. The repository history
was initialized after the project already existed, so its first commits are a
truthful dependency-ordered reconstruction of the working tree, not fabricated
historic events.

## [Unreleased]

### Added

- Owner-scoped Clerk JWT verification, Neon/Alembic workspace persistence,
  shipment drafts, trade parties, dossiers, account export/delete, and
  owner-checked PDF download routes.
- Strict no-retention trade-document intake for PDF, DOCX, XLSX, CSV, PNG, and
  JPEG with type signatures and resource limits.
- Render backend and Vercel frontend deployment artifacts for free-tier demos.
- Public SEO/PWA foundation, accessible responsive navigation, and an
  editorial responsive Shipment Desk.

### Changed

- Runtime AI provider/model configuration now documents the executable Groq
  defaults instead of claiming an unavailable provider. Historic meta
  requirements remain preserved as planning source material.
- The web form submits selected ISO corridor codes rather than visually showing
  a route while posting a hard-coded one.

### Security

- Original uploaded document bytes are never persisted; Clerk profile data and
  session/OAuth tokens are not stored by default.
- Uploads are limited to 15 MiB per file, 40 MiB per request, and 10 files.
