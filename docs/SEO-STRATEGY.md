# FreightDoc SEO strategy

## Scope and guardrails

FreightDoc is a new B2B trade-documentation workspace. Search content must explain preparation workflows, not promise customs clearance, legal eligibility, tariff accuracy, or broker services. Any page that discusses a country requirement must carry a source date and a reminder that a licensed customs broker must confirm the final filing position.

The authenticated shipment desk, generated dossiers, uploads, and Clerk entry routes are not marketing pages. They must stay out of search indexes and must never be cached as user data by the PWA service worker.

## Audience and search intent

| Audience | Job to be done | Search intent | Relevant public route or content |
| --- | --- | --- | --- |
| First-time exporter | Understand which documents they may need | Informational | `/how-it-works`, export-documentation guides |
| Operations manager | Standardize a reviewable shipment brief | Commercial investigation | Product workflow and supported-corridor pages |
| Freight forwarder or broker | Review prepared facts and exceptions | Product evaluation | Security, methodology, and later integration content |
| Technical evaluator | Assess data handling and privacy | Navigational / trust | Security and privacy pages once published |

## Current crawlable surface

The implemented public content routes are `/how-it-works` and `/supported-corridors`. The root route remains the Clerk-gated application entry point at this stage, so it must not be treated as a conventional crawlable marketing homepage. Route-aware metadata marks authentication and authenticated workspace states `noindex, nofollow`.

Before submitting a sitemap, configure `VITE_PUBLIC_SITE_URL` in Vercel with the final HTTPS custom domain and generate a sitemap using that exact origin. Do not submit a sitemap containing a guessed Vercel or product domain.

## Content pillars

1. **Export-documentation preparation** — commercial invoices, packing lists, certificates, and review workflows.
2. **HS-code classification review** — explain classification confidence, review boundaries, and source dates without giving classification advice for a particular product.
3. **Supported trade routes** — country-pair scope, destination-specific requirements, and update/review dates.
4. **Document-intake safety** — what file types are accepted, that originals are not retained, and how extracted facts require review.
5. **Operational readiness** — how exporters organize information before handing it to a customs broker or forwarder.

## Technical foundation

- Unique page title and description are set at runtime for each public route.
- Canonical URLs derive from `VITE_PUBLIC_SITE_URL` when configured, otherwise from the current browser origin for local development.
- Public pages include only truthful `Organization`, `WebSite`, `SoftwareApplication`, and `WebPage` JSON-LD. No rating, review, FAQ, price, or customer schema is emitted without real evidence.
- Open Graph and Twitter metadata use FreightDoc-owned artwork in `frontend/public/og/`.
- `robots.txt` blocks API and Clerk entry routes. Add a canonical sitemap directive only after the deployed domain is set.
- The PWA precaches static versioned assets only. It excludes videos and has no runtime rule for API data, Clerk data, uploads, or PDFs.

## E-E-A-T and source policy

Every future trade guide needs:

1. A named author or reviewer and a publication/review date.
2. Links to primary customs/trade sources for factual statements.
3. A short scope note explaining what FreightDoc does and does not decide.
4. A broker-review notice near action-oriented advice.
5. A change log when regulations, APIs, or supported corridors are updated.

Do not publish generated source summaries as though they were legal analysis. Human editorial review is required before publishing a guide.

## Measurement plan

This is a new property, so the baseline is zero and early goals are directional rather than promises.

| Metric | Baseline | 3 months | 6 months | 12 months |
| --- | --- | --- | --- | --- |
| Indexed public pages | 0 | 4–8 | 12–20 | 30+ |
| Qualified organic visits | 0 | Establish baseline | Month-over-month growth | Channel-level target after baseline |
| Organic workspace starts | 0 | Instrument | Measure conversion by route | Optimize verified conversion paths |
| Core Web Vitals | Not measured | Collect field data | Maintain good thresholds | Review every release |
| Source-reviewed guides | 0 | 3 | 8 | 18+ |

Use privacy-conscious analytics only after a product decision on consent and retention. Track page views, route-to-sign-in clicks, content freshness, and crawl errors; never send shipment content or document text to analytics.
