import DocumentTabs from './DocumentTabs';
import DownloadBar from './DownloadBar';
import './dossier-view.css';

const docName = (value) => String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
const objectOrEmpty = (value) => (value && typeof value === 'object' && !Array.isArray(value) ? value : {});
const textValue = (value, fallback) => {
  if (typeof value === 'string' && value.trim()) return value;
  if (value && typeof value === 'object') {
    const nested = value.message || value.detail;
    return typeof nested === 'string' && nested.trim() ? nested : fallback;
  }
  return fallback;
};

export default function DossierView({ result = {} }) {
  const source = objectOrEmpty(result);
  const classification = objectOrEmpty(source.classification);
  const tariff = objectOrEmpty(source.tariff);
  const requiredDocs = Array.isArray(source.required_docs) ? source.required_docs : [];
  const documents = objectOrEmpty(source.documents);
  const validation = objectOrEmpty(source.validation);
  const pdfs = objectOrEmpty(source.pdfs);
  const findings = Array.isArray(validation.errors) ? validation.errors : [];
  const readyToShip = validation.ready_to_ship === true;
  const score = Number.isFinite(Number(validation.compliance_score)) ? Number(validation.compliance_score) : 0;

  return <section className="dossier-view" aria-labelledby="dossier-title">
    <header className="dossier-header">
      <div>
        <p>SHIPMENT DOSSIER</p>
        <h2 id="dossier-title">{classification.hs_description || 'Generated shipment dossier'}</h2>
        <span>HS {classification.hs_code || 'Pending review'} · {classification.category || 'Classification pending'} · {tariff.source || 'Tariff source pending'}</span>
      </div>
      <div className={`readiness${readyToShip ? ' is-ready' : ''}`} aria-label={`Readiness score ${score} out of 100`}>
        <span>Readiness</span><b>{score}</b><small>/ 100</small>
        <strong>{readyToShip ? 'Ready for review' : 'Review required'}</strong>
      </div>
      <DownloadBar pdfs={pdfs} />
    </header>
    <div className="dossier-grid">
      <section className="dossier-summary" aria-labelledby="requirements-title">
        <h3 id="requirements-title">Shipment requirements</h3>
        <p>{requiredDocs.length} documents identified for this route. Review each document before filing.</p>
        <ul>{requiredDocs.map((document, index) => <li key={`${docName(document)}-${index}`}>{docName(document)}<span>Required</span></li>)}</ul>
        <h3>Compliance checks</h3>
        {findings.length ? <div className="finding-list">{findings.map((finding, index) => <article className={finding?.severity || ''} key={`${finding?.field || 'issue'}-${index}`}><b>{finding?.severity === 'critical' ? 'Action needed' : 'Review note'}</b><span>{textValue(finding?.issue, 'Validation issue requires review.')}</span><small>{textValue(finding?.fix, 'Review the shipment details before filing.')}</small></article>)}</div> : <div className="clear-state">No validation issues were found in the generated package.</div>}
      </section>
      <section className="dossier-documents" aria-labelledby="documents-title">
        <div className="dossier-section-head"><div><p>DOCUMENT PACKAGE</p><h3 id="documents-title">Generated filing documents</h3></div><span>{Object.keys(documents).length} prepared</span></div>
        <DocumentTabs documents={documents} requiredDocs={requiredDocs} findings={findings} />
      </section>
    </div>
    <footer className="dossier-footer"><div><p>INFORMATIONAL PREPARATION</p><span>Confirm final filing requirements with a licensed customs broker.</span></div><DownloadBar pdfs={pdfs} /></footer>
  </section>;
}
