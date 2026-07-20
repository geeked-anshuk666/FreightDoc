# Security architecture

## Identity and ownership

Clerk is the identity provider. Protected API routes validate bearer-token signing algorithm, issuer, expiry, subject, and optional audience against a cached Clerk JWKS. The persistence layer receives only the verified opaque JWT `sub`, stored as `owner_id`.

FreightDoc does **not** persist a Clerk email, name, avatar, OAuth identity, session token, or raw JWT. Every repository read includes `owner_id`; a foreign resource receives the same not-found result as a missing one to reduce ID probing. `/health`, country-pair reference data, and the stateless demo pipeline remain public; saved workspaces, documents, dossiers, and downloads are protected.

## Upload boundary

Trade documents are untrusted input. Before parsing, FreightDoc normalizes filenames, verifies extension/MIME/magic-signature agreement, and rejects unsupported, oversized, encrypted, malformed, or resource-intensive data. Office archives, PDFs, images, CSV files, and workbooks have bounded member/page/pixel/row/cell/text limits. Parsers operate in memory and return stable error codes.

Original upload bytes are discarded after scanning/extraction. They are never stored in Postgres, logs, API responses, PDFs, or the PWA cache. Only bounded metadata, reviewed extraction facts, confidence, and error/provenance records are retained until shipment deletion. Scans that require OCR return `OCR_UNAVAILABLE` unless a real bounded OCR worker is configured; FreightDoc never fabricates extracted values.

## Operational controls

- Secrets live in environment variables; source and Render/Vercel config contain variable names only.
- CORS uses explicit configured origins; wildcard credential access is not enabled.
- The single-instance free-tier deployment uses bounded in-memory endpoint limits. A multi-instance launch must introduce a shared limiter.
- Request IDs support minimal audit correlation without copying trade-document content or credentials.
- Alembic owns database schema changes; the application does not call `create_all()` at startup.

## Limits

FreightDoc is not a customs broker or a malware scanner. Optional scanner integration is a deployment decision; the free-tier baseline is strict content/resource validation. Tariff fallbacks and AI output remain labelled, informational, and subject to broker review.
