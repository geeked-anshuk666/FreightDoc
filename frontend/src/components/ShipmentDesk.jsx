import { useMemo, useState } from 'react';
import { useFreightPipeline } from '../hooks/useFreightPipeline';
import DossierView from './DossierView';
import './shipment-desk.css';

const MAX_FILES = 10;
const MAX_FILE_BYTES = 15 * 1024 * 1024;
const MAX_TOTAL_BYTES = 40 * 1024 * 1024;
const EU_MEMBER_CODES = new Set(['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']);
const SUPPORTED_BILATERAL = new Set(['US-DE', 'US-GB', 'US-IN', 'US-JP', 'US-CA', 'US-AU', 'IN-US']);

const countries = [
  ['US', 'United States'], ['IN', 'India'], ['CN', 'China'], ['AT', 'Austria'], ['BE', 'Belgium'], ['BG', 'Bulgaria'], ['HR', 'Croatia'], ['CY', 'Cyprus'], ['CZ', 'Czechia'], ['DK', 'Denmark'], ['EE', 'Estonia'], ['FI', 'Finland'], ['FR', 'France'], ['DE', 'Germany'], ['GR', 'Greece'], ['HU', 'Hungary'], ['IE', 'Ireland'], ['IT', 'Italy'], ['LV', 'Latvia'], ['LT', 'Lithuania'], ['LU', 'Luxembourg'], ['MT', 'Malta'], ['NL', 'Netherlands'], ['PL', 'Poland'], ['PT', 'Portugal'], ['RO', 'Romania'], ['SK', 'Slovakia'], ['SI', 'Slovenia'], ['ES', 'Spain'], ['SE', 'Sweden'], ['GB', 'United Kingdom'], ['JP', 'Japan'], ['CA', 'Canada'], ['AU', 'Australia'],
];

const currencies = [['USD', 'US Dollar'], ['EUR', 'Euro'], ['GBP', 'Pound Sterling'], ['INR', 'Indian Rupee']];
const locationSuggestions = {
  US: ['Port of New York / New Jersey (USNYC)', 'Port of Los Angeles (USLAX)', 'Chicago O’Hare (ORD)'],
  DE: ['Hamburg, Germany (DEHAM)', 'Frankfurt Airport (FRA)'],
  GB: ['Port of Felixstowe (GBFXT)', 'London Heathrow (LHR)'],
  IN: ['Mumbai, India (INBOM)', 'Delhi Airport (DEL)'],
  JP: ['Tokyo, Japan (JPTYO)', 'Narita Airport (NRT)'],
  CA: ['Port of Vancouver (CAVAN)', 'Toronto Pearson (YYZ)'],
  AU: ['Port of Sydney (AUSYD)', 'Melbourne Airport (MEL)'],
  CN: ['Port of Shanghai (CNSHA)', 'Shenzhen Bao’an (SZX)'],
};
const acceptedExtensions = new Set(['pdf', 'docx', 'xlsx', 'csv', 'png', 'jpg', 'jpeg']);
const stages = [['route', '01', 'Trade route'], ['cargo', '02', 'Cargo'], ['commercials', '03', 'Commercials'], ['parties', '04', 'Parties'], ['documents', '05', 'Documents'], ['review', '06', 'Review']];

const formatBytes = (size) => `${(size / (1024 * 1024)).toFixed(size >= 10 * 1024 * 1024 ? 0 : 1)} MiB`;
const countryName = (code) => countries.find(([candidate]) => candidate === code)?.[1] || code;
const locationList = (country) => locationSuggestions[country] || ['Add a port, airport, or city for internal route context'];

function Field({ label, hint, children, wide = false }) {
  return <label className={`desk-field${wide ? ' is-wide' : ''}`}><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function routeError(originCountry, destinationCountry) {
  if (originCountry === 'CN' && !EU_MEMBER_CODES.has(destinationCountry)) return 'China exports require a specific EU member-state destination.';
  if (originCountry !== 'CN' && !SUPPORTED_BILATERAL.has(`${originCountry}-${destinationCountry}`)) return 'This route is not in the current FreightDoc corridor set. Choose one of the supported country pairs.';
  return '';
}

function fileIssue(file) {
  const extension = file.name.split('.').pop()?.toLowerCase();
  if (!extension || !acceptedExtensions.has(extension)) return `${file.name}: use PDF, DOCX, XLSX, CSV, PNG, or JPG.`;
  if (file.size > MAX_FILE_BYTES) return `${file.name}: exceeds the 15 MiB per-file limit.`;
  return '';
}

function PipelineFailure({ failure, loading, canRetry, onRetry }) {
  if (!failure) return null;

  return (
    <section className="run-error" role="alert" aria-live="assertive" aria-atomic="true">
      <div className="run-error-copy">
        <p className="run-error-kicker">DOSSIER PREPARATION PAUSED</p>
        <h3>We couldn’t prepare the dossier.</h3>
        <p>{failure.message}</p>
        <p className="run-error-guidance">{failure.retryGuidance}</p>
      </div>
      {(failure.stageLabel || failure.requestId) && (
        <dl className="run-error-details">
          {failure.stageLabel && <div><dt>Step</dt><dd>{failure.stageLabel}</dd></div>}
          {failure.requestId && <div><dt>Reference</dt><dd><code>{failure.requestId}</code></dd></div>}
        </dl>
      )}
      {canRetry && <button type="button" className="run-error-retry" onClick={onRetry} disabled={loading}>{loading ? 'Retrying dossier…' : 'Try again'} <i aria-hidden="true">→</i></button>}
    </section>
  );
}

export default function ShipmentDesk() {
  const { run, retry, canRetry, loading, error: pipelineError, result } = useFreightPipeline();
  const [activeStage, setActiveStage] = useState('route');
  const [files, setFiles] = useState([]);
  const [fileNotice, setFileNotice] = useState('');
  const [formError, setFormError] = useState('');
  const [contextOpen, setContextOpen] = useState(() => window.matchMedia('(min-width: 761px)').matches);
  const [form, setForm] = useState({
    originCountry: 'US', originLocation: 'Port of New York / New Jersey (USNYC)', destinationCountry: 'DE', destinationLocation: 'Hamburg, Germany (DEHAM)',
    productName: 'Bluetooth earbuds', productDescription: '500 wireless Bluetooth earbuds in retail packaging.', categoryHint: 'Electronics',
    quantity: '500', declaredValue: '25000', currency: 'USD', exporterName: 'Demo Exporter', importerName: 'Demo Importer', shippingContext: 'Ocean freight',
  });

  const corridorMessage = useMemo(() => routeError(form.originCountry, form.destinationCountry), [form.originCountry, form.destinationCountry]);
  const selectedOriginLocations = useMemo(() => locationList(form.originCountry), [form.originCountry]);
  const selectedDestinationLocations = useMemo(() => locationList(form.destinationCountry), [form.destinationCountry]);
  const totalFileBytes = files.reduce((total, file) => total + file.size, 0);
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const handleCountryChange = (key, value) => {
    update(key, value);
    setFormError('');
  };

  const handleFileSelection = (event) => {
    const additions = Array.from(event.target.files || []);
    const next = [...files];
    const messages = [];
    additions.forEach((file) => {
      const issue = fileIssue(file);
      if (issue) { messages.push(issue); return; }
      if (next.length >= MAX_FILES) { messages.push(`Only ${MAX_FILES} files can be queued at one time.`); return; }
      if (next.reduce((total, item) => total + item.size, 0) + file.size > MAX_TOTAL_BYTES) { messages.push(`Adding ${file.name} would exceed the 40 MiB selection limit.`); return; }
      next.push(file);
    });
    setFiles(next);
    setFileNotice(messages.join(' '));
    event.target.value = '';
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const issue = routeError(form.originCountry, form.destinationCountry);
    if (issue) { setFormError(issue); document.getElementById('desk-route')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
    setFormError('');
    run({
      product_name: form.productName,
      product_description: form.productDescription,
      origin_country: form.originCountry,
      destination_country: form.destinationCountry,
      quantity: Number(form.quantity),
      declared_value: Number(form.declaredValue),
      currency: form.currency,
      exporter_name: form.exporterName,
      importer_name: form.importerName,
    });
  };

  return (
    <>
      <section id="workflow" className="shipment-desk" aria-labelledby="shipment-desk-title">
        <header className="desk-intro">
          <p>SHIPMENT DESK</p>
          <h2 id="shipment-desk-title">Build the route. We’ll build the dossier.</h2>
          <span>Give FreightDoc the facts that travel with the shipment. Review each result before filing.</span>
        </header>

        <form className="desk-frame" onSubmit={handleSubmit}>
          <aside className="desk-stepper" aria-label="Shipment preparation stages">
            <div className="desk-stepper-title"><span>PREPARE</span><strong>Shipment brief</strong></div>
            <ol>{stages.map(([id, number, label]) => <li key={id} className={activeStage === id ? 'is-active' : ''}><a href={`#desk-${id}`} aria-current={activeStage === id ? 'step' : undefined} onClick={() => setActiveStage(id)}><span>{number}</span><b>{label}</b></a></li>)}</ol>
            <p>Only the core shipment facts are sent to the dossier pipeline.</p>
          </aside>

          <div className="desk-form">
            <section id="desk-route" className="desk-section" onFocusCapture={() => setActiveStage('route')}>
              <div className="desk-section-title"><p>01 / TRADE ROUTE</p><h3>Start with the countries.</h3><span>Country codes drive corridor rules. Location details help your own preparation and are not submitted to the pipeline.</span></div>
              <div className="desk-fields desk-route-fields">
                <Field label="Origin country">
                  <select value={form.originCountry} onChange={(event) => handleCountryChange('originCountry', event.target.value)} required>{countries.map(([code, name]) => <option value={code} key={code}>{name} ({code})</option>)}</select>
                </Field>
                <Field label="Destination country">
                  <select value={form.destinationCountry} onChange={(event) => handleCountryChange('destinationCountry', event.target.value)} required>{countries.map(([code, name]) => <option value={code} key={code}>{name} ({code})</option>)}</select>
                </Field>
                <Field label="Origin location" hint="Optional context — not sent to the pipeline.">
                  <input value={form.originLocation} onChange={(event) => update('originLocation', event.target.value)} list="origin-location-options" placeholder="Port, airport, or city" maxLength="160" />
                  <datalist id="origin-location-options">{selectedOriginLocations.map((location) => <option key={location} value={location} />)}</datalist>
                </Field>
                <Field label="Destination location" hint="Optional context — not sent to the pipeline.">
                  <input value={form.destinationLocation} onChange={(event) => update('destinationLocation', event.target.value)} list="destination-location-options" placeholder="Port, airport, or city" maxLength="160" />
                  <datalist id="destination-location-options">{selectedDestinationLocations.map((location) => <option key={location} value={location} />)}</datalist>
                </Field>
              </div>
              <div className={`desk-route-status${corridorMessage ? ' is-warning' : ''}`} role={corridorMessage ? 'alert' : 'status'}><strong>{countryName(form.originCountry)} → {countryName(form.destinationCountry)}</strong><span>{corridorMessage || 'Supported corridor. The country-rule checklist will be resolved during dossier preparation.'}</span></div>
            </section>

            <section id="desk-cargo" className="desk-section" onFocusCapture={() => setActiveStage('cargo')}>
              <div className="desk-section-title"><p>02 / CARGO</p><h3>Describe what is moving.</h3><span>Use the product’s commercial description. FreightDoc will prepare an HS-code suggestion for review.</span></div>
              <div className="desk-fields">
                <Field label="Goods" hint="Required for classification."><input value={form.productName} onChange={(event) => update('productName', event.target.value)} minLength="2" maxLength="160" required /></Field>
                <Field label="Cargo description" wide hint="Include material, function, quantity or packaging details that distinguish the goods."><textarea value={form.productDescription} onChange={(event) => update('productDescription', event.target.value)} minLength="10" maxLength="3000" required /></Field>
              </div>
            </section>

            <section id="desk-commercials" className="desk-section" onFocusCapture={() => setActiveStage('commercials')}>
              <div className="desk-section-title"><p>03 / COMMERCIALS</p><h3>Give the package a value.</h3><span>These figures travel into the preparation workflow. Check them against your commercial records before continuing.</span></div>
              <div className="desk-fields desk-commercial-fields">
                <Field label="Quantity"><input type="number" inputMode="numeric" value={form.quantity} onChange={(event) => update('quantity', event.target.value)} min="1" max="1000000" step="1" required /></Field>
                <Field label="Declared value"><input type="number" inputMode="decimal" value={form.declaredValue} onChange={(event) => update('declaredValue', event.target.value)} min="0.01" max="100000000" step="0.01" required /></Field>
                <Field label="Currency"><select value={form.currency} onChange={(event) => update('currency', event.target.value)} required>{currencies.map(([code, name]) => <option key={code} value={code}>{code} — {name}</option>)}</select></Field>
              </div>
            </section>

            <section id="desk-parties" className="desk-section" onFocusCapture={() => setActiveStage('parties')}>
              <div className="desk-section-title"><p>04 / PARTIES</p><h3>Name the commercial parties.</h3><span>These names are included in the generated document package. Add the legal business names where possible.</span></div>
              <div className="desk-fields">
                <Field label="Exporter"><input value={form.exporterName} onChange={(event) => update('exporterName', event.target.value)} minLength="2" maxLength="160" required /></Field>
                <Field label="Importer"><input value={form.importerName} onChange={(event) => update('importerName', event.target.value)} minLength="2" maxLength="160" required /></Field>
              </div>
            </section>

            <details className="desk-context" open={contextOpen} onToggle={(event) => setContextOpen(event.currentTarget.open)}>
              <summary>Show optional planning context <span>Not sent to the current dossier pipeline</span></summary>
              <div className="desk-context-fields">
                <Field label="Commodity category hint"><input value={form.categoryHint} onChange={(event) => update('categoryHint', event.target.value)} maxLength="120" placeholder="For your own review" /></Field>
                <Field label="Shipping method"><input value={form.shippingContext} onChange={(event) => update('shippingContext', event.target.value)} maxLength="120" placeholder="For your own review" /></Field>
              </div>
            </details>

            <section id="desk-documents" className="desk-section desk-document-section" onFocusCapture={() => setActiveStage('documents')}>
              <div className="desk-section-title"><p>05 / DOCUMENT INTAKE</p><h3>Bring the paperwork you already have.</h3><span>Files are selected locally first. The intake service verifies every file again before any extraction.</span></div>
              <div className="desk-upload-grid">
                <label className="desk-dropzone">
                  <input type="file" multiple accept=".pdf,.docx,.xlsx,.csv,image/png,image/jpeg" onChange={handleFileSelection} />
                  <strong>Choose supporting documents</strong>
                  <span>PDF, DOCX, XLSX, CSV, PNG, or JPG</span>
                  <b>Browse files</b>
                </label>
                <div className="desk-upload-rules"><strong>Intake limits</strong><span>15 MiB per file</span><span>40 MiB per selection</span><span>Up to 10 files</span><small>Original bytes are not retained after secure extraction. Never upload a password-protected or unrelated document.</small></div>
              </div>
              {fileNotice && <p className="desk-file-notice" role="alert">{fileNotice}</p>}
              {files.length > 0 && <ul className="desk-file-list" aria-label="Locally queued documents">{files.map((file, index) => <li key={`${file.name}-${file.lastModified}-${index}`}><span><b>{file.name}</b><small>{formatBytes(file.size)} · queued locally</small></span><button type="button" aria-label={`Remove ${file.name}`} onClick={() => setFiles((current) => current.filter((_, fileIndex) => fileIndex !== index))}>Remove</button></li>)}</ul>}
              <p className="desk-file-summary">{files.length} of {MAX_FILES} files selected · {formatBytes(totalFileBytes)} of 40 MiB</p>
            </section>

            <footer id="desk-review" className="desk-review" onFocusCapture={() => setActiveStage('review')}>
              <div><p>06 / REVIEW</p><strong>{countryName(form.originCountry)} → {countryName(form.destinationCountry)}</strong><span>{form.productName || 'Add a product description'} · {form.quantity || '0'} units · {form.currency} {form.declaredValue || '0'}</span></div>
              <button type="submit" disabled={loading || Boolean(corridorMessage)}>{loading ? 'Preparing dossier…' : 'Prepare shipment dossier'} <i aria-hidden="true">→</i></button>
            </footer>
            {formError && <p className="desk-submit-error" role="alert">{formError}</p>}
            <PipelineFailure failure={pipelineError} loading={loading} canRetry={canRetry} onRetry={retry} />
          </div>
        </form>
      </section>
      {result && <DossierView result={result} />}
    </>
  );
}
