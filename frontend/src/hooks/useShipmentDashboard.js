import { useAuth } from '@clerk/react';
import { useCallback, useEffect, useState } from 'react';

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function readableError(response, body) {
  if (response.status === 401 || response.status === 403) return 'Your session needs to be refreshed before FreightDoc can load saved shipments.';
  return body?.detail?.message || body?.detail || body?.message || 'Saved shipments are unavailable right now.';
}

export function useShipmentDashboard() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [state, setState] = useState({ status: 'loading', shipments: [], message: '' });

  const refresh = useCallback(async () => {
    if (!isLoaded || !isSignedIn) return;
    setState((current) => ({ ...current, status: 'loading', message: '' }));
    try {
      const token = await getToken();
      const response = await fetch(`${apiBaseUrl}/api/shipments?limit=12`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'omit',
      });
      const body = await response.json().catch(() => null);
      if (!response.ok || !Array.isArray(body?.items)) throw new Error(readableError(response, body));
      setState({ status: 'ready', shipments: body.items, message: '' });
    } catch (error) {
      setState({ status: 'unavailable', shipments: [], message: error instanceof Error ? error.message : 'Saved shipments are unavailable right now.' });
    }
  }, [getToken, isLoaded, isSignedIn]);

  useEffect(() => { refresh(); }, [refresh]);
  return { ...state, refresh };
}
