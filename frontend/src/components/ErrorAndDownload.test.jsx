import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('jszip', () => ({
  default: class FakeZip {
    file() {}
    generateAsync() { return Promise.resolve(new Blob(['zip'])); }
  },
}));

import ErrorPanel from './ErrorPanel';
import WarningPanel from './WarningPanel';
import DownloadBar from './DownloadBar';

describe('validation panels and download states', () => {
  it('renders safe issue and fix text and acknowledgement action', () => {
    const onAcknowledge = vi.fn();
    render(<><ErrorPanel errors={[{ issue: { message: 'Missing origin' }, fix: { detail: 'Add the origin country' } }]} onAcknowledge={onAcknowledge} /><WarningPanel errors={[{ issue: 'Check value', fix: 'Confirm invoice' }]} /></>);
    expect(screen.getByRole('alert')).toHaveTextContent('Missing origin');
    expect(screen.getByRole('alert')).toHaveTextContent('Fix: Add the origin country');
    expect(screen.getByRole('status')).toHaveTextContent('Check value');
    fireEvent.click(screen.getByRole('button', { name: /Acknowledge/ }));
    expect(onAcknowledge).toHaveBeenCalledTimes(1);
  });

  it('reports a missing PDF package without attempting a download', () => {
    render(<DownloadBar pdfs={{}} />);
    fireEvent.click(screen.getByRole('button', { name: /Download dossier package/ }));
    expect(screen.getByRole('alert')).toHaveTextContent('PDF package is not available yet');
    expect(screen.getByRole('button', { name: /Download dossier package/ })).not.toBeDisabled();
  });

  it('bundles available PDFs and reports the started download', async () => {
    render(<DownloadBar pdfs={{ invoice: 'cGRm' }} />);
    fireEvent.click(screen.getByRole('button', { name: /Download dossier package/ }));
    expect(screen.getByRole('button', { name: /Preparing download/ })).toBeDisabled();
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Complete dossier download started.'));
  });
});
