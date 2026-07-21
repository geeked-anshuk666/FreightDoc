import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '@clerk/react';
import { getOptionalShipmentReview, postOptionalReviewAction } from '../lib/shipmentReviewApi';
import './shipment-review-workspace.css';

const label = (value) => String(value || '').replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) || 'Unspecified';
const text = (value, fallback = 'No details provided.') => typeof value === 'string' && value.trim() ? value : fallback;
const severity = (value) => ['critical', 'warning', 'info'].includes(value) ? value : 'info';

function localFindings(result) {
  const validation = result?.validation || {};
  const known = Array.isArray(validation.errors) ? validation.errors : [];
  const findings = known.map((item, index) => ({ id: `validation-${index}`, severity: severity(item?.severity), title: text(item?.issue), next: text(item?.fix, 'Review the shipment brief and record your decision.'), source: 'Deterministic validation' }));
  if (!result?.classification?.hs_code) findings.push({ id: 'classification', severity: 'warning', title: 'Classification remains unconfirmed', next: 'Confirm or manually enter an HS classification before final review.', source: 'Shipment brief' });
  if (!Array.isArray(result?.required_docs) || !result.required_docs.length) findings.push({ id: 'documents', severity: 'warning', title: 'Required document checklist is incomplete', next: 'Add or verify the route-specific document requirements.', source: 'Route rules' });
  return findings;
}

export default function ShipmentReviewWorkspace({ result }) {
  const { getToken } = useAuth();
  const shipmentId = result?.shipment_id || result?.id;
  const [remote, setRemote] = useState({ available: false, reason: 'Loading canonical record…' });
  const [filter, setFilter] = useState('all');
  const [resolved, setResolved] = useState([]);
  const [notice, setNotice] = useState('');
  useEffect(() => { let active = true; getOptionalShipmentReview(shipmentId, getToken).then((data) => active && setRemote(data)); return () => { active = false; }; }, [shipmentId, getToken]);
  const findings = remote.available && remote.findings?.length ? remote.findings.map((item, index) => ({ id: item.id || `quality-${index}`, severity: severity(item.severity), title: text(item.message || item.title), next: text(item.remediation || item.next_step, 'Review this finding and record your decision.'), source: text(item.rule_name || item.source, 'Quality rule') })) : localFindings(result);
  const visible = useMemo(() => findings.filter((item) => filter === 'all' || item.severity === filter).filter((item) => !resolved.includes(item.id)), [findings, filter, resolved]);
  const facts = remote.facts || [];
  const revisions = remote.revisions || [];
  const tasks = remote.tasks || [];
  const workflows = remote.workflows || [];
  const suggestions = remote.suggestions || [];
  const decide = async (finding, action) => { setResolved((current) => [...current, finding.id]); setNotice(`${action === 'waive' ? 'Waived' : 'Marked for review'}: ${finding.title}. Add a reason in the saved review record when it is available.`); };
  const suggestionAction = async (suggestion, decision) => { const ok = suggestion?.id && await postOptionalReviewAction(`/api/v1/suggestions/${encodeURIComponent(suggestion.id)}/${decision}`, {}, getToken); setNotice(ok ? `Suggestion ${decision}ed and sent for review.` : 'Suggestion action is unavailable. No fact was changed.'); };
  return <section className="review-workspace" aria-labelledby="review-workspace-title">
    <header><div><p>REVIEW WORKSPACE</p><h2 id="review-workspace-title">Pre-flight, evidence, and decisions</h2><span>All readiness checks are informational preparation. A human must review and approve any final dossier.</span></div><b className={remote.available ? 'record-live' : 'record-local'}>{remote.available ? 'Canonical record connected' : 'Local deterministic review'}</b></header>
    {!remote.available && <p className="review-fallback" role="status">{remote.reason} Manual review and deterministic checks remain available.</p>}
    {notice && <p className="review-notice" role="status">{notice}</p>}
    <div className="review-grid">
      <section className="review-card quality-card"><div className="review-card-head"><div><p>READINESS</p><h3>Pre-flight findings</h3></div><div className="filter-group" aria-label="Filter findings">{['all', 'critical', 'warning', 'info'].map((item) => <button type="button" key={item} className={filter === item ? 'active' : ''} onClick={() => setFilter(item)}>{item === 'all' ? 'All' : label(item)}</button>)}</div></div>{visible.length ? <ol className="preflight-list">{visible.map((item) => <li key={item.id} className={`severity-${item.severity}`}><div><b>{label(item.severity)}</b><strong>{item.title}</strong><span>{item.next}</span><small>Source: {item.source}</small></div><div className="finding-actions"><button type="button" onClick={() => decide(item, 'review')}>Review</button><button type="button" onClick={() => decide(item, 'waive')}>Waive</button></div></li>)}</ol> : <p className="review-empty">No open findings match this filter. Keep the dossier under human review before use.</p>}</section>
      <section className="review-card"><p>CANONICAL RECORD</p><h3>Facts & revision history</h3>{facts.length ? <ol className="fact-list">{facts.map((fact, index) => <li key={fact.id || index}><strong>{label(fact.name || fact.key)}</strong><span>{text(fact.display_value || fact.value, 'Value withheld')}</span><small>Source: {text(fact.source_name || fact.source, 'Manual entry')} · Rev {fact.revision_number || 'current'} · {fact.confidence != null ? `${Math.round(Number(fact.confidence) * 100)}% confidence` : 'human review required'}</small></li>)}</ol> : <p className="review-empty">No canonical facts are available yet. Use the shipment brief and supporting evidence to create or correct facts once record sync is enabled.</p>}{revisions.length > 0 && <ol className="fact-list" aria-label="Shipment revision history">{revisions.slice(0, 4).map((revision, index) => <li key={revision.id || index}><strong>Revision {revision.revision_number || index + 1}</strong><span>{text(revision.reason || revision.summary, 'Human edit or review decision')}</span><small>{text(revision.created_by_name || revision.actor, 'Recorded user')} · {text(revision.created_at, 'timestamp pending')}</small></li>)}</ol>}<button type="button" className="subtle-action" onClick={() => setNotice('Manual fact editing requires a saved canonical record; no local fact was changed.')}>Add manual fact</button></section>
      <section className="review-card"><p>DECISION QUEUE</p><h3>Assigned review tasks</h3>{tasks.length ? <ol className="task-list">{tasks.map((task, index) => <li key={task.id || index}><strong>{text(task.title || task.reason, 'Review required')}</strong><span>{label(task.status || 'open')} · {text(task.assigned_to_name || task.assigned_to, 'Unassigned')}</span><small>{text(task.reason, 'No reason provided.')}</small></li>)}</ol> : <p className="review-empty">No synced tasks. Findings above can be reviewed or waived with a reason when a saved record is available.</p>}</section>
      <section className="review-card"><p>DOCUMENT WORKFLOW</p><h3>Dependencies & duplicates</h3>{workflows.length ? <ol className="workflow-list">{workflows.map((workflow, index) => <li key={workflow.id || index}><strong>{text(workflow.document_name || workflow.name, 'Document')}</strong><span>{label(workflow.status || 'pending')}</span><small>{workflow.duplicate_of ? 'Possible duplicate — keep, replace, or link after review.' : text(workflow.blocker || workflow.dependency, 'No dependency details available.')}</small></li>)}</ol> : <p className="review-empty">Document workflow status will appear after intake. Duplicate detection is hash-based and never deletes a document automatically.</p>}</section>
    </div>
    {suggestions.length > 0 && <section className="ai-suggestions" aria-labelledby="ai-suggestions-title"><div><p>OPTIONAL AI</p><h3 id="ai-suggestions-title">Reviewable suggestions</h3><span>Suggestions never change a fact or approval without your explicit decision.</span></div><ol>{suggestions.map((suggestion, index) => <li key={suggestion.id || index}><div><strong>{text(suggestion.title || suggestion.field, 'Suggested update')}</strong><span>{text(suggestion.rationale || suggestion.explanation)}</span><small>Provenance: {text(suggestion.provider || suggestion.source, 'Optional AI')} · Confidence: {suggestion.confidence == null ? 'not supplied' : `${Math.round(Number(suggestion.confidence) * 100)}%`}</small></div><div><button type="button" onClick={() => suggestionAction(suggestion, 'accept')}>Accept</button><button type="button" onClick={() => suggestionAction(suggestion, 'reject')}>Reject</button></div></li>)}</ol></section>}
    <footer>Record decisions with a reason. “Review-ready” means internally prepared for review—not filed, cleared, screened, or legal advice.</footer>
  </section>;
}
