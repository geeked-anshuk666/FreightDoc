# FreightDoc SEO implementation roadmap

## Phase 1 — foundation (weeks 1–4)

- [x] Establish public `How it works` and `Supported corridors` pages.
- [x] Add route-aware title, description, canonical, social metadata, and conservative JSON-LD.
- [x] Mark Clerk entry and authenticated workspace views `noindex`.
- [x] Add a static-only PWA policy and update/offline user messaging.
- [ ] Configure the final `VITE_PUBLIC_SITE_URL` value in Vercel.
- [ ] Generate and submit a host-specific sitemap only after the final domain is known.
- [ ] Add Search Console and privacy-reviewed analytics.

## Phase 2 — source-reviewed expansion (weeks 5–12)

- Publish the first four reviewed resource guides from the content calendar.
- Add privacy, security, and product-methodology pages after their implementation docs are finalized.
- Establish page templates that require source links, review dates, author/reviewer, and broker-review notice.
- Validate mobile accessibility, Core Web Vitals, and crawl coverage after each public-page release.

## Phase 3 — measured scale (weeks 13–24)

- Use Search Console queries and user interviews to prioritize resource clusters.
- Build only verified corridor guides for which ownership, sources, and review cadence exist.
- Improve internal linking from educational guides to the product method and supported corridors.
- Test content-to-sign-in journeys without tracking private shipment inputs.

## Phase 4 — authority and maintenance (months 7–12)

- Publish dated methodology updates and original, reviewable research only where data rights permit.
- Conduct a verified competitor and keyword-gap study before any comparison content.
- Refresh trade-source dates, corridor status, and model/provider explanations on a defined schedule.
- Review structured data and crawl directives after architectural changes.

## Release gates

No public SEO release is complete until the page has an accurate title/description, keyboard and mobile checks, no unsupported claims, reviewer/date information, source links where factual claims are made, and a tested `noindex` boundary for the app and auth routes.
