import { useState } from 'react';

const DEFAULT_ERROR_MESSAGE = 'We could not prepare the dossier right now. Please try again shortly.';

const RETRYABLE_CODES = new Set([
  'AI_SERVICE_ERROR',
  'AI_MALFORMED_RESPONSE',
  'AI_RATE_LIMITED',
  'PIPELINE_PROCESSING_ERROR',
]);

const NON_RETRYABLE_CODES = new Set([
  'AI_CONFIGURATION_ERROR',
  'PIPELINE_INPUT_INVALID',
]);

const STAGE_LABELS = {
  classification: 'Product classification',
  requirements: 'Document requirements',
  tariff_lookup: 'Tariff lookup',
  generation: 'Document generation',
  validation: 'Document validation',
  pdf_rendering: 'PDF preparation',
  pipeline: 'Dossier preparation',
};

function asRecord(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : null;
}

function asText(value) {
  if (typeof value !== 'string') return '';
  return value.replace(/\s+/g, ' ').trim().slice(0, 500);
}

function firstText(values) {
  return values.map(asText).find(Boolean) || '';
}

function errorRecords(body) {
  const root = asRecord(body);
  if (!root) return [];

  const detail = asRecord(root.detail);
  const nestedError = asRecord(root.error);
  const nestedDetail = asRecord(nestedError?.detail);

  return [detail, nestedDetail, nestedError, root].filter(Boolean);
}

function errorField(records, field) {
  return firstText(records.map((record) => record[field]));
}

function errorBoolean(records, field) {
  for (const record of records) {
    if (typeof record[field] === 'boolean') return record[field];
  }
  return null;
}

function fallbackMessage(code, status) {
  if (code === 'AI_CONFIGURATION_ERROR') return 'The dossier service needs attention before it can prepare this shipment. Keep the reference ID handy if you contact support.';
  if (code === 'PIPELINE_INPUT_INVALID') return 'Some shipment details could not be processed. Review them and submit the dossier again.';
  if (code === 'AI_RATE_LIMITED' || status === 429) return 'The dossier service is busy at the moment. Please try again shortly.';
  return DEFAULT_ERROR_MESSAGE;
}

function retryGuidance(code, retryable) {
  if (retryable) return 'Your shipment details and selected documents are still available. You can try the same dossier again.';
  if (code === 'PIPELINE_INPUT_INVALID') return 'Review the shipment details, then submit the dossier again.';
  return 'Your shipment details and selected documents are still available. Keep the reference ID if you need help from support.';
}

export function formatPipelineStage(stage) {
  const normalized = asText(stage).toLowerCase().replace(/[\s-]+/g, '_');
  if (!normalized) return '';
  if (STAGE_LABELS[normalized]) return STAGE_LABELS[normalized];
  return normalized.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function parsePipelineError(body, status = 0) {
  const records = errorRecords(body);
  const root = asRecord(body);
  const code = errorField(records, 'code');
  const stage = errorField(records, 'stage');
  const requestId = firstText([
    ...records.map((record) => record.request_id),
    ...records.map((record) => record.requestId),
    ...records.map((record) => record.correlation_id),
  ]);
  const explicitRetryable = errorBoolean(records, 'retryable');
  const suppliedMessage = firstText([
    ...records.map((record) => record.message),
    root?.detail,
    root?.error,
    body,
  ]);
  const retryable = explicitRetryable ?? (
    !NON_RETRYABLE_CODES.has(code) && (
      RETRYABLE_CODES.has(code)
      || status === 0
      || status === 408
      || status === 425
      || status === 429
      || status >= 500
    )
  );

  return {
    code,
    message: suppliedMessage || fallbackMessage(code, status),
    requestId,
    retryable,
    retryGuidance: retryGuidance(code, retryable),
    stage,
    stageLabel: formatPipelineStage(stage),
    status,
  };
}

function connectionError() {
  return {
    code: 'NETWORK_ERROR',
    message: 'We could not reach the dossier service. Check your connection and try again.',
    requestId: '',
    retryable: true,
    retryGuidance: retryGuidance('NETWORK_ERROR', true),
    stage: '',
    stageLabel: '',
    status: 0,
  };
}

export function useFreightPipeline() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [lastPayload, setLastPayload] = useState(null);

  async function run(payload = lastPayload) {
    if (!payload) return null;

    setLastPayload(payload);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/full-pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const body = await response.json().catch(() => null);

      if (!response.ok) {
        setError(parsePipelineError(body, response.status));
        return null;
      }

      setResult(body);
      return body;
    } catch {
      setError(connectionError());
      return null;
    } finally {
      setLoading(false);
    }
  }

  function retry() {
    return run(lastPayload);
  }

  return { run, retry, canRetry: Boolean(error?.retryable && lastPayload), loading, error, result };
}
