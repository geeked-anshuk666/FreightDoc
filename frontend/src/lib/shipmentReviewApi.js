const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
const CANONICAL_API_PREFIX = '/api/v1';

const object = (value) => value && typeof value === 'object' && !Array.isArray(value) ? value : null;
const array = (value) => Array.isArray(value) ? value : [];

export async function getOptionalShipmentReview(shipmentId, getToken) {
  if (!shipmentId) return { available: false, reason: 'No saved shipment record is available for this package.' };
  try {
    const token = getToken ? await getToken() : null;
    const response = await fetch(`${API_BASE_URL}${CANONICAL_API_PREFIX}/shipments/${encodeURIComponent(shipmentId)}/record`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}, credentials: 'omit',
    });
    const body = await response.json().catch(() => null);
    if (!response.ok || !object(body)) return { available: false, reason: 'The canonical record service is not available for this shipment yet.' };
    return {
      available: true,
      record: body,
      facts: array(body.facts), revisions: array(body.revisions), tasks: array(body.review_tasks),
      workflows: array(body.document_workflows), suggestions: array(body.suggestions), findings: array(body.quality_findings),
    };
  } catch {
    return { available: false, reason: 'Canonical record data is temporarily unavailable. The local pre-flight remains available.' };
  }
}

export async function postOptionalReviewAction(path, payload, getToken) {
  try {
    const token = getToken ? await getToken() : null;
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      credentials: 'omit', body: JSON.stringify(payload || {}),
    });
    return response.ok;
  } catch { return false; }
}
