import MainNavigation from './MainNavigation';
import PageMetadata from './PageMetadata';
import './public-information.css';

const corridors = [
  ['United States', 'Germany'],
  ['United States', 'United Kingdom'],
  ['United States', 'India'],
  ['United States', 'Japan'],
  ['United States', 'Canada'],
  ['United States', 'Australia'],
  ['India', 'United States'],
  ['China', 'A specific EU member state'],
];

const process = [
  ['01', 'Brief the shipment', 'Provide the product description, route, quantity, declared value, currency, and parties involved.'],
  ['02', 'Classify with review signals', 'FreightDoc prepares an HS-code suggestion with confidence information for human review.'],
  ['03', 'Collect source context', 'Tariff and trade-data retrieval is labeled with source, retrieval time, and fallback status.'],
  ['04', 'Resolve document requirements', 'A versioned country-rule configuration identifies the documentation to prepare for a supported corridor.'],
  ['05', 'Prepare and cross-check', 'FreightDoc drafts a structured package and highlights mismatches for a licensed customs broker to review.'],
];

const siteUrl = () => (import.meta.env.VITE_PUBLIC_SITE_URL || window.location.origin).replace(/\/$/, '');

function publicSchema(path, pageTitle, pageDescription) {
  const origin = siteUrl();
  return {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Organization',
        name: 'FreightDoc',
        url: origin,
        logo: `${origin}/favicon.svg`,
        description: 'A web workspace for preparing reviewable export-documentation packages.',
      },
      {
        '@type': 'WebSite',
        name: 'FreightDoc',
        url: origin,
      },
      {
        '@type': 'SoftwareApplication',
        name: 'FreightDoc',
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Web',
        url: `${origin}${path}`,
        description: pageDescription,
      },
      {
        '@type': 'WebPage',
        name: pageTitle,
        url: `${origin}${path}`,
        description: pageDescription,
      },
    ],
  };
}

function BrokerReviewNotice() {
  return <aside className="broker-review-notice" aria-label="Important legal review notice"><strong>Preparation support, not filing advice.</strong><span>Confirm classification, tariff treatment, and final filing requirements with a licensed customs broker.</span></aside>;
}

export default function PublicInformationPage({ page }) {
  const isCorridors = page === 'corridors';
  const path = isCorridors ? '/supported-corridors' : '/how-it-works';
  const title = isCorridors ? 'Supported export corridors' : 'How FreightDoc works';
  const description = isCorridors
    ? 'See the export corridors FreightDoc currently supports for structured shipment-documentation preparation.'
    : 'Learn how FreightDoc turns a shipment brief into a reviewable export-documentation package for supported corridors.';

  return (
    <div className="public-information-page">
      <PageMetadata title={title} description={description} jsonLd={publicSchema(path, title, description)} />
      <MainNavigation variant="public" />
      <main className="public-information-main" id="main-content">
        <header className="public-information-hero">
          <p>{isCorridors ? 'SUPPORTED TRADE ROUTES' : 'DOCUMENTATION WORKFLOW'}</p>
          <h1>{isCorridors ? 'Start with the route. Build toward a reviewable dossier.' : 'From shipment brief to broker-reviewable dossier.'}</h1>
          <span>{isCorridors ? 'FreightDoc currently supports a defined set of origin–destination corridors. Each route is resolved against its versioned rule set.' : 'A structured workflow keeps AI-assisted classification distinct from deterministic tariff, rules, and PDF stages.'}</span>
          <a className="public-primary-link" href="/sign-in">Prepare a shipment <strong aria-hidden="true">→</strong></a>
        </header>

        {isCorridors ? (
          <section className="corridor-section" aria-labelledby="corridor-title">
            <div className="public-section-heading"><p>AVAILABLE NOW</p><h2 id="corridor-title">Eight supported pathways</h2></div>
            <ol className="corridor-list">
              {corridors.map(([origin, destination], index) => <li key={`${origin}-${destination}`}><span>{String(index + 1).padStart(2, '0')}</span><strong>{origin}</strong><i aria-hidden="true">→</i><b>{destination}</b></li>)}
            </ol>
            <p className="public-detail">For China exports, choose the actual EU member-state destination; an ambiguous “EU” destination cannot be resolved into a country-specific document set.</p>
            <BrokerReviewNotice />
          </section>
        ) : (
          <>
            <section className="process-section" aria-labelledby="process-title">
              <div className="public-section-heading"><p>THE FREIGHTDOC METHOD</p><h2 id="process-title">A clear handoff between information, automation, and review.</h2></div>
              <ol className="process-list">
                {process.map(([number, heading, copy]) => <li key={number}><span>{number}</span><div><h3>{heading}</h3><p>{copy}</p></div></li>)}
              </ol>
            </section>
            <BrokerReviewNotice />
          </>
        )}
      </main>
    </div>
  );
}
