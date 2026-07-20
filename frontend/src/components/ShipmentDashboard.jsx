import { useShipmentDashboard } from '../hooks/useShipmentDashboard';
import './shipment-dashboard.css';

const STATUS_COPY = {
  draft: ['Draft', 'Finish the brief before generating a dossier.'],
  processing: ['Processing', 'FreightDoc is preparing its review package.'],
  needs_review: ['Needs review', 'Resolve blockers before this dossier is handed off.'],
  review_ready: ['Review ready', 'A reviewer can now inspect the versioned dossier.'],
  archived: ['Archived', 'This shipment is retained as a read-only record.'],
};

function formatDate(value) {
  if (!value) return 'Recently created';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Recently created';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
}

function shipmentTitle(shipment) {
  return shipment.title?.trim() || 'Untitled shipment brief';
}

export default function ShipmentDashboard() {
  const { status, shipments, message, refresh } = useShipmentDashboard();

  return (
    <main className="shipment-dashboard" id="main-content">
      <header className="dashboard-hero">
        <div>
          <p>MY SHIPMENTS</p>
          <h1>Keep every shipment<br /><em>review-ready.</em></h1>
          <span>Prepare the facts, surface the exceptions, then create a dossier your customs reviewer can act on.</span>
        </div>
        <a className="dashboard-create" href="/#workflow">Prepare a shipment <strong aria-hidden="true">→</strong></a>
      </header>

      <section className="dashboard-summary" aria-label="Shipment workspace summary">
        <article><span>Active briefs</span><strong>{status === 'ready' ? shipments.filter((shipment) => shipment.status !== 'archived').length : '—'}</strong><small>Drafts, processing, and review work</small></article>
        <article><span>Review ready</span><strong>{status === 'ready' ? shipments.filter((shipment) => shipment.status === 'review_ready').length : '—'}</strong><small>Packages ready for human handoff</small></article>
        <article><span>Operating principle</span><strong>Review first</strong><small>FreightDoc is informational—not filing advice.</small></article>
      </section>

      <section className="dashboard-list" aria-labelledby="recent-shipments-title">
        <header>
          <div><p>WORK QUEUE</p><h2 id="recent-shipments-title">Recent shipments</h2></div>
          <button type="button" onClick={refresh} disabled={status === 'loading'}>{status === 'loading' ? 'Refreshing…' : 'Refresh'}</button>
        </header>

        {status === 'loading' && <div className="dashboard-loading" role="status"><span /><b>Loading your shipment workspace…</b></div>}

        {status === 'unavailable' && (
          <div className="dashboard-unavailable" role="status">
            <div><strong>Saved shipments are temporarily unavailable.</strong><span>{message} You can still prepare a new dossier from the shipment desk.</span></div>
            <a href="/#workflow">Open shipment desk</a>
          </div>
        )}

        {status === 'ready' && shipments.length === 0 && (
          <div className="dashboard-empty">
            <p>YOUR QUEUE IS CLEAR</p>
            <h3>Start with one shipment brief.</h3>
            <span>FreightDoc will turn its route, cargo, commercial values, and supporting facts into a reviewable document package.</span>
            <a href="/#workflow">Prepare your first shipment <strong aria-hidden="true">→</strong></a>
          </div>
        )}

        {status === 'ready' && shipments.length > 0 && (
          <ol className="shipment-cards">
            {shipments.map((shipment) => {
              const [label, helper] = STATUS_COPY[shipment.status] || ['In progress', 'Review the shipment details before moving forward.'];
              return <li key={shipment.id}>
                <a href={`/#workflow`} aria-label={`Open ${shipmentTitle(shipment)}`}>
                  <span className={`shipment-status status-${shipment.status}`}>{label}</span>
                  <div><strong>{shipmentTitle(shipment)}</strong><small>{helper}</small></div>
                  <span className="shipment-signals" aria-label={`${shipment.document_count || 0} documents${shipment.readiness_score == null ? '' : `, readiness ${shipment.readiness_score} out of 100`}${shipment.blocker_count ? `, ${shipment.blocker_count} blockers` : ''}${shipment.warning_count ? `, ${shipment.warning_count} warnings` : ''}`}>
                    <b>{shipment.document_count || 0} docs</b>
                    {shipment.readiness_score != null && <b>{shipment.readiness_score}/100</b>}
                    {shipment.blocker_count > 0 && <b className="is-blocked">{shipment.blocker_count} blockers</b>}
                    {shipment.warning_count > 0 && <b>{shipment.warning_count} warnings</b>}
                  </span>
                  <time dateTime={shipment.updated_at || shipment.created_at || undefined}>{formatDate(shipment.updated_at || shipment.created_at)}</time>
                  <i aria-hidden="true">→</i>
                </a>
              </li>;
            })}
          </ol>
        )}
      </section>
    </main>
  );
}
