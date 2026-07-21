import { act, renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { parsePipelineError, formatPipelineStage, useFreightPipeline } from './useFreightPipeline';

describe('parsePipelineError', () => {
  it('normalizes nested API details and retry metadata', () => {
    expect(parsePipelineError({ detail: { code: 'AI_RATE_LIMITED', stage: 'tariff_lookup', request_id: 'req-7', message: 'Busy' } }, 429)).toMatchObject({
      code: 'AI_RATE_LIMITED', message: 'Busy', requestId: 'req-7', retryable: true, stageLabel: 'Tariff lookup', status: 429,
    });
  });

  it('protects the UI from object, array, and oversized error values', () => {
    const parsed = parsePipelineError({ error: { detail: { issue: { unsafe: true } } } }, 400);
    expect(parsed.message).toBe('We could not prepare the dossier right now. Please try again shortly.');
    expect(parsed.message).not.toContain('[object Object]');
    expect(formatPipelineStage('pdf-rendering')).toBe('PDF preparation');
    expect(formatPipelineStage('')).toBe('');
  });

  it('keeps explicit non-retryable responses non-retryable', () => {
    expect(parsePipelineError({ code: 'PIPELINE_INPUT_INVALID', retryable: false }, 422)).toMatchObject({ retryable: false, code: 'PIPELINE_INPUT_INVALID' });
  });
});

describe('useFreightPipeline', () => {
  beforeEach(() => vi.restoreAllMocks());

  it('resets stale result before a new request and exposes retry', async () => {
    const payload = { product_name: 'Earbuds' };
    let resolveFirst;
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ shipment: 'old' }) })
      .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }))
      .mockResolvedValueOnce({ ok: false, status: 503, json: async () => ({ code: 'PIPELINE_PROCESSING_ERROR' }) })
    );
    const { result } = renderHook(() => useFreightPipeline());

    await act(async () => { await result.current.run(payload); });
    expect(result.current.result).toEqual({ shipment: 'old' });
    let pending;
    await act(async () => { pending = result.current.run(payload); });
    expect(result.current.result).toBeNull();
    resolveFirst({ ok: true, json: async () => ({ shipment: 'new' }) });
    await act(async () => { await pending; });
    expect(result.current.result).toEqual({ shipment: 'new' });

    await act(async () => { await result.current.run(payload); });
    await waitFor(() => expect(result.current.canRetry).toBe(true));
    expect(result.current.error.code).toBe('PIPELINE_PROCESSING_ERROR');
    await act(async () => { await result.current.retry(); });
    expect(fetch).toHaveBeenCalledTimes(4);
  });

  it('turns connection failures into a retryable user message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    const { result } = renderHook(() => useFreightPipeline());
    await act(async () => { await result.current.run({ product_name: 'x' }); });
    expect(result.current.error).toMatchObject({ code: 'NETWORK_ERROR', retryable: true, status: 0 });
    expect(result.current.canRetry).toBe(true);
  });
});
