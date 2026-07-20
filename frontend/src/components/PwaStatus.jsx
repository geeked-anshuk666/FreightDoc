import { useEffect, useState } from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';
import './pwa-status.css';

export default function PwaStatus() {
  const [online, setOnline] = useState(() => navigator.onLine);
  const [dismissed, setDismissed] = useState(false);
  const { needRefresh: [needRefresh], offlineReady: [offlineReady], updateServiceWorker } = useRegisterSW();

  useEffect(() => {
    const onOnline = () => { setOnline(true); setDismissed(false); };
    const onOffline = () => { setOnline(false); setDismissed(false); };
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
  }, []);

  if (dismissed || (online && !needRefresh && !offlineReady)) return null;
  const isOffline = !online;
  const label = isOffline
    ? 'You are offline. FreightDoc can show the application shell, but shipment records, uploads, and dossiers are never stored offline.'
    : needRefresh
      ? 'A new FreightDoc version is ready.'
      : 'FreightDoc is ready for limited offline access.';

  return (
    <aside className="pwa-status" role="status" aria-live="polite">
      <span>{label}</span>
      <div>
        {needRefresh && <button type="button" onClick={() => updateServiceWorker(true)}>Update now</button>}
        <button type="button" className="pwa-dismiss" onClick={() => setDismissed(true)} aria-label="Dismiss application status">Dismiss</button>
      </div>
    </aside>
  );
}
