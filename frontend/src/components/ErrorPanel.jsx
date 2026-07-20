function message(value, fallback) {
  if (typeof value === 'string' && value.trim()) return value;
  if (value && typeof value === 'object') {
    const nested = value.message || value.detail;
    return typeof nested === 'string' && nested.trim() ? nested : fallback;
  }
  return fallback;
}

export default function ErrorPanel({ errors = [], acknowledged = false, onAcknowledge }) {
  if (!Array.isArray(errors) || errors.length === 0) return null;
  return <section className="critical" role="alert" aria-labelledby="critical-issues-title">
    <h2 id="critical-issues-title">Critical issues</h2>
    {errors.map((error, index) => <p key={index}>{message(error?.issue, 'A validation issue needs review.')} <span>Fix: {message(error?.fix, 'Review the shipment details and try again.')}</span></p>)}
    {!acknowledged && <button type="button" onClick={onAcknowledge}>Acknowledge and enable download</button>}
  </section>;
}
