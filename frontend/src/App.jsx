import { Show } from '@clerk/react';
import AuthExperience from './components/AuthExperience';
import FullscreenCargoStory from './components/FullscreenCargoStory';
import MainNavigation from './components/MainNavigation';
import PageMetadata from './components/PageMetadata';
import PublicInformationPage from './components/PublicInformationPage';
import PwaStatus from './components/PwaStatus';
import ShipmentDesk from './components/ShipmentDesk';
import ShipmentDashboard from './components/ShipmentDashboard';
import './components/cargo-story-resilience.css';

function ShipmentWorkspace() {
  return (
    <>
      <FullscreenCargoStory>
        <p>INTELLIGENCE FOR GLOBAL CARGO</p>
        <h1>Move trade<br /><em>with certainty.</em></h1>
        <span>From a product brief to a reviewable export dossier — before the container is sealed.</span>
        <a className="hero-cta" href="#workflow">Prepare a shipment <strong>↘</strong></a>
        <div className="hero-note"><span>US → DE / LIVE ROUTE</span><span>DOCUMENTS · TARIFFS · REVIEW</span></div>
      </FullscreenCargoStory>
      <ShipmentDesk />
    </>
  );
}

export default function App() {
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  const hasClerkKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY?.startsWith('pk_');

  if (path === '/how-it-works') return <><PwaStatus /><PublicInformationPage page="how-it-works" /></>;
  if (path === '/supported-corridors') return <><PwaStatus /><PublicInformationPage page="corridors" /></>;
  if (path === '/sign-in' || path === '/sign-up') return <><PageMetadata noIndex title={path === '/sign-in' ? 'Sign in' : 'Create an account'} description="Access the FreightDoc shipment workspace." /><PwaStatus /><AuthExperience mode={path.slice(1)} /></>;
  if (!hasClerkKey) return <><PageMetadata noIndex title="Sign in" description="Access the FreightDoc shipment workspace." /><AuthExperience mode="sign-in" /></>;

  return (
    <>
      <PwaStatus />
      <Show when="loading"><PageMetadata noIndex title="Loading workspace" description="Loading the FreightDoc shipment workspace." /><AuthExperience mode="sign-in" loading /></Show>
      <Show when="signed-out"><PageMetadata noIndex title="Sign in" description="Access the FreightDoc shipment workspace." /><AuthExperience mode="sign-in" /></Show>
      <Show when="signed-in">
        <PageMetadata noIndex title={path === '/dashboard' ? 'My shipments' : 'Shipment workspace'} description="Prepare a reviewable export-documentation package in FreightDoc." />
        <main className="freight-platform">
          <MainNavigation />
          {path === '/dashboard' ? <ShipmentDashboard /> : <ShipmentWorkspace />}
        </main>
      </Show>
    </>
  );
}
