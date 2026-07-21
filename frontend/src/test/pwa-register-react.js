export function useRegisterSW() {
  const state = globalThis.__PWA_TEST_STATE__ || { needRefresh: false, offlineReady: false };
  return {
    needRefresh: [state.needRefresh],
    offlineReady: [state.offlineReady],
    updateServiceWorker: globalThis.__PWA_TEST_UPDATE__ || (() => {}),
  };
}
