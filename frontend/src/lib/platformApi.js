const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
const record = (v) => v && typeof v === 'object' && !Array.isArray(v) ? v : null;
export async function optionalPlatform(path, getToken) {
  try { const token = await getToken?.(); const r = await fetch(`${BASE}/api/v1${path}`, { headers: token ? { Authorization: `Bearer ${token}` } : {}, credentials: 'omit' }); const body = await r.json().catch(() => null); return r.ok && record(body) ? { available: true, data: body } : { available: false }; } catch { return { available: false }; }
}
