import { useEffect, useRef, useState } from 'react';
import { SignIn, SignUp } from '@clerk/react';
import './auth-experience.css';

const media = ['/media/freightdoc-port-01.mp4', '/media/freightdoc-port-02.mp4'];
const captions = ['From product brief to shipment-ready documentation.', 'Built for trade that moves across borders.'];

const clerkAppearance = {
  layout: { socialButtonsPlacement: 'top', socialButtonsVariant: 'iconButton' },
  variables: { colorPrimary: '#f06432', colorBackground: '#0b1b26', colorText: '#f8fbf7', colorTextSecondary: '#a9c0c8', colorInputBackground: '#122934', colorInputText: '#f8fbf7', borderRadius: '4px', fontFamily: 'Arial, Helvetica Neue, sans-serif' },
  elements: {
    rootBox: 'fd-clerk-root', card: 'fd-clerk-card', header: 'fd-clerk-header', headerTitle: 'fd-clerk-title', headerSubtitle: 'fd-clerk-subtitle', socialButtonsBlock: 'fd-clerk-social-block', socialButtonsBlockButton: 'fd-clerk-social', dividerRow: 'fd-clerk-divider-row', dividerLine: 'fd-clerk-divider', dividerText: 'fd-clerk-divider-text', formFieldLabel: 'fd-clerk-label', formFieldInput: 'fd-clerk-input', formFieldHintText: 'fd-clerk-hint', formFieldErrorText: 'fd-clerk-error', formFieldWarningText: 'fd-clerk-warning', formFieldAction: 'fd-clerk-field-action', formFieldInputShowPasswordButton: 'fd-clerk-password-toggle', formButtonPrimary: 'fd-clerk-primary', footer: 'fd-clerk-footer', footerActionText: 'fd-clerk-footer-text', footerActionLink: 'fd-clerk-link', identityPreviewEditButton: 'fd-clerk-link', identityPreviewText: 'fd-clerk-guidance', alert: 'fd-clerk-alert-box', alertText: 'fd-clerk-alert', otpCodeFieldInput: 'fd-clerk-input', modalCloseButton: 'fd-clerk-link',
  },
};

function ProviderIcon({ provider }) {
  if (provider === 'github') return <svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .7a11.3 11.3 0 0 0-3.58 22.02c.57.1.77-.24.77-.54v-2.13c-3.14.68-3.8-1.33-3.8-1.33-.52-1.32-1.26-1.67-1.26-1.67-1.03-.7.08-.69.08-.69 1.14.08 1.74 1.17 1.74 1.17 1.01 1.73 2.66 1.23 3.3.94.1-.74.4-1.24.72-1.52-2.5-.28-5.13-1.25-5.13-5.57 0-1.23.44-2.24 1.17-3.03-.12-.29-.51-1.43.11-2.98 0 0 .95-.31 3.12 1.16A10.8 10.8 0 0 1 12 6.2c.96 0 1.92.13 2.82.38 2.16-1.47 3.11-1.16 3.11-1.16.63 1.55.23 2.69.12 2.98.72.79 1.16 1.8 1.16 3.03 0 4.33-2.63 5.28-5.14 5.56.41.35.77 1 .77 2.02v3.18c0 .3.2.65.78.54A11.3 11.3 0 0 0 12 .7Z" /></svg>;
  if (provider === 'microsoft') return <svg aria-hidden="true" viewBox="0 0 24 24"><path fill="#f35325" d="M1 1h10.5v10.5H1z" /><path fill="#81bc06" d="M12.5 1H23v10.5H12.5z" /><path fill="#05a6f0" d="M1 12.5h10.5V23H1z" /><path fill="#ffba08" d="M12.5 12.5H23V23H12.5z" /></svg>;
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1Z" /><path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.65l-3.57-2.77c-.98.66-2.24 1.06-3.71 1.06-2.86 0-5.28-1.93-6.15-4.52H2.18A11 11 0 0 0 12 23Z" /><path fill="#fbbc05" d="M5.85 14.12A6.62 6.62 0 0 1 5.5 12c0-.74.13-1.45.35-2.12V7.02H2.18A11 11 0 0 0 1 12c0 1.77.42 3.45 1.18 4.98l3.67-2.86Z" /><path fill="#ea4335" d="M12 5.36c1.62 0 3.08.56 4.23 1.66l3.17-3.17C17.45 2.03 14.97 1 12 1a11 11 0 0 0-9.82 6.02l3.67 2.86C6.72 7.29 9.14 5.36 12 5.36Z" /></svg>;
}

function OAuthProviderButtons() {
  const fallbackPosition = { google: 0, github: 1, microsoft: 2 };
  const providers = ['google', 'github', 'microsoft'];
  const findProviderButtons = () => {
    const buttons = [...document.querySelectorAll('.auth-clerk-stage button')];
    return providers.reduce((mapped, provider, index) => {
      const match = buttons.find((button) => button.matches(`.cl-socialButtonsIconButton__${provider}, .cl-button__${provider}`) || `${button.getAttribute('aria-label') || ''} ${button.getAttribute('title') || ''} ${button.getAttribute('data-localization-key') || ''} ${button.textContent || ''}`.toLowerCase().includes(provider));
      mapped[provider] = match || buttons[index];
      return mapped;
    }, {});
  };
  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      Object.entries(findProviderButtons()).forEach(([provider, button]) => {
        if (!button) return;
        button.dataset.fdSocialProvider = provider;
        button.classList.add('fd-original-social');
      });
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);
  const triggerProvider = (provider) => {
    const button = document.querySelector(`.auth-clerk-stage [data-fd-social-provider="${provider}"]`) || findProviderButtons()[provider];
    (button || [...document.querySelectorAll('.auth-clerk-stage button')][fallbackPosition[provider]])?.click();
  };
  return <><div className="fd-oauth-row" role="group" aria-label="Continue with a social account">{[['google', 'Google'], ['github', 'GitHub'], ['microsoft', 'Microsoft']].map(([provider, label]) => <button key={provider} type="button" className={`fd-oauth-button fd-oauth-${provider}`} onClick={() => triggerProvider(provider)}><ProviderIcon provider={provider} /><span>{label}</span></button>)}</div><div className="fd-oauth-divider" aria-hidden="true"><i /><span>or</span><i /></div></>;
}

function CinematicMedia() {
  const refs = [useRef(null), useRef(null)];
  const [active, setActive] = useState(0);
  const switching = useRef(false);
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined;
    const videos = refs.map((ref) => ref.current);
    const switchTo = (from) => {
      if (switching.current) return;
      switching.current = true;
      const nextIndex = 1 - from; const next = videos[nextIndex]; const current = videos[from];
      next.currentTime = 0; next.play().catch(() => undefined); setActive(nextIndex);
      window.setTimeout(() => { current.pause(); current.currentTime = 0; switching.current = false; }, 760);
    };
    const cleanup = videos.map((video, index) => {
      const time = () => { if (Number.isFinite(video.duration) && video.duration - video.currentTime < .78) switchTo(index); };
      video.addEventListener('timeupdate', time); video.addEventListener('ended', () => switchTo(index));
      return () => video.removeEventListener('timeupdate', time);
    });
    videos[0]?.play().catch(() => undefined);
    return () => { cleanup.forEach((remove) => remove()); videos.forEach((video) => video?.pause()); };
  }, []);
  return <div className="auth-media" aria-hidden="true">{media.map((source, index) => <video key={source} ref={refs[index]} className={active === index ? 'auth-video is-active' : 'auth-video'} src={source} muted playsInline preload={index === 0 ? 'metadata' : 'none'} />)}<div className="auth-video-tint" /><div className="auth-video-grain" /><div className="auth-brand"><a href="/">FREIGHT<span>DOC</span></a><span>GLOBAL TRADE INTELLIGENCE</span></div><div className="auth-media-copy"><p>INTELLIGENCE FOR GLOBAL CARGO</p><h1>Move trade<br /><em>with certainty.</em></h1><span>Prepare, review, and move shipment documentation with confidence.</span><small>{captions[active]}</small></div><div className="auth-media-index"><span>01</span><i /><span>02</span></div></div>;
}

export default function AuthExperience({ mode, loading = false }) {
  const isSignUp = mode === 'sign-up';
  const keyConfigured = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY?.startsWith('pk_');
  const clerkForm = isSignUp ? <SignUp routing="hash" signInUrl="/sign-in" fallbackRedirectUrl="/" appearance={clerkAppearance} /> : <SignIn routing="hash" signUpUrl="/sign-up" fallbackRedirectUrl="/" appearance={clerkAppearance} />;
  return <main className="auth-page"><section className="auth-visual"><CinematicMedia /></section><section className="auth-panel"><a className="auth-mobile-brand" href="/">FREIGHT<span>DOC</span></a><div className="auth-form-wrap"><p className="auth-eyebrow">{isSignUp ? 'CREATE YOUR WORKSPACE' : 'FREIGHTDOC WORKSPACE'}</p><h2>{loading ? 'Opening your secure workspace.' : isSignUp ? 'Start moving trade with certainty.' : 'Welcome back.'}</h2><p className="auth-intro">{loading ? 'Connecting to secure sign-in...' : isSignUp ? 'Create your account to prepare and manage shipments.' : 'Sign in to continue to your FreightDoc workspace.'}</p>{loading ? <div className="auth-config-state"><b>Loading secure sign-in</b><span>If this remains on screen, check your internet connection and refresh.</span></div> : keyConfigured ? <><OAuthProviderButtons /><div className="auth-clerk-stage">{clerkForm}</div></> : <div className="auth-config-state"><b>Clerk needs one final local setting.</b><span>Add <code>VITE_CLERK_PUBLISHABLE_KEY</code> to <code>frontend/.env.local</code>, then restart Vite.</span></div>}<a className="auth-back" href="/">&larr; Back to FreightDoc</a></div></section></main>;
}
