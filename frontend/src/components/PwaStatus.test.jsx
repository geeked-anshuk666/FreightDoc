import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const updateServiceWorker = vi.fn();
let registrationState;

import PwaStatus from './PwaStatus';

describe('PwaStatus', () => {
  beforeEach(() => {
    registrationState = { needRefresh: false, offlineReady: false };
    updateServiceWorker.mockReset();
    globalThis.__PWA_TEST_STATE__ = registrationState;
    globalThis.__PWA_TEST_UPDATE__ = updateServiceWorker;
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false });
  });

  it('announces offline limitations and can be dismissed', () => {
    render(<PwaStatus />);
    expect(screen.getByRole('status')).toHaveTextContent('You are offline');
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss application status' }));
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('offers the service-worker update action when a refresh is available', () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true });
    registrationState.needRefresh = true;
    render(<PwaStatus />);
    fireEvent.click(screen.getByRole('button', { name: 'Update now' }));
    expect(updateServiceWorker).toHaveBeenCalledWith(true);
  });
});
