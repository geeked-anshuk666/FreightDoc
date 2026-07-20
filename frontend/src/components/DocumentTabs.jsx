import { useState } from 'react';
const title = (value) => String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
const textValue = (value, fallback) => {
  if (typeof value === 'string' && value.trim()) return value;
  if (value && typeof value === 'object') {
    const nested = value.message || value.detail;
    return typeof nested === 'string' && nested.trim() ? nested : fallback;
  }
  return fallback;
};
function DocumentCard({ name, fields, required, findings = [] }) {
  const [open, setOpen] = useState(false);
  const panelId = `document-panel-${name.replace(/[^a-z0-9_-]/gi, '-')}`;
  const issues = findings.filter((item) => item?.document?.toLowerCase().replaceAll(' ', '_') === name || item?.document === 'package');
  const values = Object.entries(fields || {}).filter(([, value]) => value !== null && value !== undefined && value !== '');
  return <article className="document-card">
    <button className="document-card-head" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open} aria-controls={panelId}>
      <span className="document-state">{issues.some((issue) => issue?.severity === 'critical') ? 'Needs review' : 'Generated'}</span>
      <strong>{title(name)}</strong><small>{required ? 'Required for this shipment' : 'Supporting document'}</small>
      <i aria-hidden="true">{open ? '−' : '+'}</i>
    </button>
    {open && <div id={panelId} className="document-card-body" role="region" aria-label={`${title(name)} details`}>
      <div className="document-field-grid">{values.slice(0, 8).map(([key, value]) => <div key={key}><span>{title(key)}</span><b>{typeof value === 'object' ? 'Provided in document' : String(value)}</b></div>)}</div>
      {issues.length > 0 && <div className="document-issues">{issues.map((issue, index) => <p key={`${issue?.field || 'issue'}-${index}`}><b>{title(issue?.field)}:</b> {textValue(issue?.fix, 'Review this field before filing.')}</p>)}</div>}
    </div>}
  </article>;
}
export default function DocumentTabs({ documents = {}, requiredDocs = [], findings = [] }) { const required = new Set(requiredDocs); return <section className="document-list" aria-label="Generated shipment documents">{Object.entries(documents || {}).filter(([, document]) => document).map(([name, fields]) => <DocumentCard key={name} name={name} fields={fields} required={required.has(name)} findings={findings} />)}</section>; }
