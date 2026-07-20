import { useEffect, useRef, useState } from 'react';
import { UserButton, useClerk } from '@clerk/react';
import './main-navigation.css';

function WorkspaceControls({ onNavigate }) {
  const { signOut } = useClerk();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut({ redirectUrl: '/sign-in' });
    } finally {
      setIsSigningOut(false);
      onNavigate?.();
    }
  };

  return (
    <div className="main-nav-account">
      <UserButton appearance={{ elements: { avatarBox: 'main-nav-avatar' } }} />
      <button className="main-nav-signout" type="button" onClick={handleSignOut} disabled={isSigningOut}>
        {isSigningOut ? 'Signing out…' : 'Sign out'}
      </button>
    </div>
  );
}

export default function MainNavigation({ variant = 'workspace' }) {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const firstLinkRef = useRef(null);
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  const isPublic = variant === 'public';
  const homeHref = path === '/' ? '#top' : '/';
  const shipmentHref = path === '/' ? '#workflow' : '/#workflow';

  useEffect(() => {
    const syncScrollState = () => setScrolled(window.scrollY > 20);
    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setOpen(false);
    };
    syncScrollState();
    window.addEventListener('scroll', syncScrollState, { passive: true });
    window.addEventListener('keydown', closeOnEscape);
    return () => {
      window.removeEventListener('scroll', syncScrollState);
      window.removeEventListener('keydown', closeOnEscape);
    };
  }, []);

  useEffect(() => {
    if (open) firstLinkRef.current?.focus();
  }, [open]);

  const closeMenu = () => setOpen(false);
  const active = (href) => (path === href ? ' is-current' : '');

  return (
    <header className={`main-navigation ${isPublic ? 'is-public' : ''} ${scrolled ? 'is-scrolled' : ''}`}>
      <a className="main-nav-brand" href={homeHref} aria-label="FreightDoc home" onClick={closeMenu}>
        FREIGHT<span>DOC</span>
      </a>
      <button
        className="main-nav-toggle"
        type="button"
        aria-label={open ? 'Close navigation menu' : 'Open navigation menu'}
        aria-controls="freightdoc-primary-navigation"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <span aria-hidden="true" />
        <span aria-hidden="true" />
      </button>
      <nav id="freightdoc-primary-navigation" className={`main-nav-links ${open ? 'is-open' : ''}`} aria-label="Primary navigation">
        <a ref={firstLinkRef} href={shipmentHref} onClick={closeMenu}>Shipment desk</a>
        <a className={active('/how-it-works')} href="/how-it-works" onClick={closeMenu}>How it works</a>
        <a className={active('/supported-corridors')} href="/supported-corridors" onClick={closeMenu}>Supported corridors</a>
        {isPublic ? (
          <a className="main-nav-signin-link" href="/sign-in" onClick={closeMenu}>Sign in</a>
        ) : (
          <WorkspaceControls onNavigate={closeMenu} />
        )}
      </nav>
    </header>
  );
}
