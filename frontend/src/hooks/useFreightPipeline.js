import { useState } from 'react';

export function useFreightPipeline() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  async function run(payload) {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/full-pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const body = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = body?.detail || body?.message || body?.error?.message;
        throw new Error(detail || `The dossier request could not be completed (${response.status}).`);
      }
      setResult(body);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'The dossier request could not be completed.');
    } finally {
      setLoading(false);
    }
  }

  return { run, loading, error, result };
}
