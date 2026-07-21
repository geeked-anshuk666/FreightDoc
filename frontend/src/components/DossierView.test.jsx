import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import DossierView from './DossierView';
import DocumentTabs from './DocumentTabs';

describe('DossierView and document accordions', () => {
  it('renders a defensive empty dossier without leaking raw JSON', () => {
    render(<DossierView result={{ classification: { hs_description: { unsafe: true } }, validation: { errors: [{ issue: { detail: 'bad' } }] } }} />);
    expect(screen.getByRole('heading', { name: 'Generated shipment dossier' })).toBeInTheDocument();
    expect(screen.getByText('bad')).toBeInTheDocument();
    expect(document.body.textContent).not.toContain('[object Object]');
    expect(screen.getByLabelText('Readiness score 0 out of 100')).toHaveTextContent('Review required');
  });

  it('opens a document panel with accessible expanded state and bounded fields', () => {
    render(<DocumentTabs documents={{ commercial_invoice: { invoice_number: 'INV-1', nested: { secret: true }, empty: '' } }} requiredDocs={['commercial_invoice']} />);
    const button = screen.getByRole('button', { name: /Commercial Invoice/ });
    expect(button).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('region', { name: 'Commercial Invoice details' })).toBeInTheDocument();
    expect(screen.getByText('Provided in document')).toBeInTheDocument();
    expect(screen.queryByText('secret')).not.toBeInTheDocument();
    fireEvent.click(button);
    expect(screen.queryByRole('region', { name: 'Commercial Invoice details' })).not.toBeInTheDocument();
  });
});
