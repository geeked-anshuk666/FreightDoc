import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const run = vi.fn();
const retry = vi.fn();
let pipelineState;
vi.mock('../hooks/useFreightPipeline', () => ({
  useFreightPipeline: () => ({ ...pipelineState, run, retry }),
}));

import ShipmentDesk from './ShipmentDesk';

describe('ShipmentDesk', () => {
  beforeEach(() => {
    run.mockReset();
    retry.mockReset();
    pipelineState = { canRetry: false, loading: false, error: null, result: null };
  });

  it('submits only the core shipment fields', async () => {
    const { container } = render(<ShipmentDesk />);
    fireEvent.submit(container.querySelector('form.desk-frame'));
    await waitFor(() => expect(run).toHaveBeenCalledWith(expect.objectContaining({
      product_name: 'Bluetooth earbuds', origin_country: 'US', destination_country: 'DE', quantity: 500, declared_value: 25000,
    })));
    expect(run.mock.calls[0][0]).not.toHaveProperty('originLocation');
    expect(run.mock.calls[0][0]).not.toHaveProperty('categoryHint');
  });

  it('blocks unsupported corridors and exposes the warning as an alert', () => {
    render(<ShipmentDesk />);
    fireEvent.change(screen.getByLabelText('Destination country'), { target: { value: 'CN' } });
    expect(screen.getByRole('alert')).toHaveTextContent('not in the current FreightDoc corridor set');
    expect(screen.getByRole('button', { name: /Prepare shipment dossier/ })).toBeDisabled();
    expect(run).not.toHaveBeenCalled();
  });

  it('rejects unsupported and oversized local files while accepting valid files', () => {
    const { container } = render(<ShipmentDesk />);
    const input = container.querySelector('input[type="file"]');
    const invalid = new File(['x'], 'malware.exe', { type: 'application/octet-stream' });
    fireEvent.change(input, { target: { files: [invalid] } });
    expect(screen.getByRole('alert')).toHaveTextContent('use PDF, DOCX, XLSX, CSV, PNG, or JPG');

    const valid = new File(['pdf'], 'invoice.pdf', { type: 'application/pdf' });
    fireEvent.change(input, { target: { files: [valid] } });
    expect(screen.getByLabelText('Locally queued documents')).toHaveTextContent('invoice.pdf');
    expect(screen.getByText(/1 of 10 files selected/)).toBeInTheDocument();
  });
});
