# FreightDoc site structure

## Implemented routes

| URL | Audience | Indexing | Purpose |
| --- | --- | --- | --- |
| `/how-it-works` | Prospective users | Indexable | Explains the preparation workflow and review boundary |
| `/supported-corridors` | Prospective users | Indexable | Lists the eight currently supported routes |
| `/sign-in` | Existing users | `noindex, nofollow` | Clerk sign-in experience |
| `/sign-up` | New users | `noindex, nofollow` | Clerk sign-up experience |
| `/` | Signed-in users / app entry | `noindex, nofollow` at runtime | Cargo story and shipment workspace |

The indexable routes are real client-side pages, not navigation placeholders. The app currently uses Vite SPA routing, so Vercel must keep its existing rewrite to `index.html` for those routes.

## Next public pages — only after source and ownership checks

```text
/product
/security
/privacy
/terms
/resources/
  /resources/export-documentation-guide
  /resources/hs-code-classification-guide
  /resources/export-to-germany-guide
  /resources/export-to-uk-guide
```

Do not add any of these to a sitemap or main navigation until a complete, source-reviewed page exists.

## Internal-link model

```text
How it works ──────┐
                    ├── Prepare a shipment / Clerk entry
Supported corridors ┘

Future resources ──> How it works
Future resources ──> Supported corridors (when route-specific)
Future security ───> Privacy / product methodology
```

## Sitemap and canonical rule

`VITE_PUBLIC_SITE_URL` is the single source for the deployed canonical origin used by the browser metadata layer. The final sitemap must contain absolute URLs only for the two implemented public routes until more content has been built. Do not publish guessed Vercel preview URLs, authentication URLs, shipment pages, dossiers, upload endpoints, or API routes in a sitemap.
