import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('@clerk/react', () => ({
  SignIn: () => <div data-testid="clerk-sign-in">Clerk sign in</div>,
  SignUp: () => <div data-testid="clerk-sign-up">Clerk sign up</div>,
}));

import AuthExperience from './AuthExperience';

describe('AuthExperience', () => {
  it('renders the loading shell without invoking Clerk while auth is pending', () => {
    render(<AuthExperience mode="sign-in" loading />);
    expect(screen.getByRole('heading', { name: 'Opening your secure workspace.' })).toBeInTheDocument();
    expect(screen.getByText('Loading secure sign-in')).toBeInTheDocument();
    expect(screen.queryByTestId('clerk-sign-in')).not.toBeInTheDocument();
  });

  it('renders the configured sign-in shell with accessible provider controls', () => {
    render(<AuthExperience mode="sign-in" />);
    expect(screen.getByRole('heading', { name: 'Welcome back.' })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: 'Continue with a social account' })).toBeInTheDocument();
    expect(screen.getByTestId('clerk-sign-in')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Back to FreightDoc/ })).toHaveAttribute('href', '/');
  });
});
