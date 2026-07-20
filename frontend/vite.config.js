import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'prompt',
      injectRegister: false,
      includeAssets: ['favicon.svg', 'icons/freightdoc-app-icon.svg', 'og/freightdoc-og.svg'],
      manifest: {
        name: 'FreightDoc — Global trade intelligence',
        short_name: 'FreightDoc',
        description: 'Prepare reviewable export dossiers before the container is sealed.',
        display: 'standalone',
        theme_color: '#091923',
        background_color: '#f4f0e8',
        start_url: '/',
        scope: '/',
        icons: [
          { src: '/icons/freightdoc-app-icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any maskable' },
          { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
        ],
        shortcuts: [
          { name: 'Shipment desk', short_name: 'Shipment desk', url: '/#workflow', icons: [{ src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }] },
          { name: 'Supported corridors', short_name: 'Corridors', url: '/supported-corridors', icons: [{ src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }] },
        ],
        screenshots: [{ src: '/og/freightdoc-og.svg', sizes: '1200x630', type: 'image/svg+xml', form_factor: 'wide', label: 'FreightDoc shipment documentation workspace' }],
      },
      workbox: {
        globPatterns: ['**/*.{html,js,css,ico,png,svg,webmanifest}'],
        globIgnores: ['**/media/**', '**/*.mp4'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/sign-in$/, /^\/sign-up$/],
        runtimeCaching: [],
        cleanupOutdatedCaches: true,
        clientsClaim: true,
        skipWaiting: false,
      },
    }),
  ],
});
