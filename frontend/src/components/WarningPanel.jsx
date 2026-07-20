const message = (value, fallback) => {
  if (typeof value === 'string' && value.trim()) return value;
  if (value && typeof value === 'object') {
    const nested = value.message || value.detail;
    return typeof nested === 'string' && nested.trim() ? nested : fallback;
  }
  return fallback;
};

export default function WarningPanel({ errors = [] }) {
  if (!Array.isArray(errors) || errors.length === 0) return null;
  return <section className="warning" role="status" aria-labelledby="warning-panel-title">
    <h2 id="warning-panel-title">Review warnings</h2>
    {errors.map((error, index) => <p key={index}>{message(error?.issue, 'A review note needs attention.')} <span>Fix: {message(error?.fix, 'Review this field before filing.')}</span></p>)}
  </section>;
}
