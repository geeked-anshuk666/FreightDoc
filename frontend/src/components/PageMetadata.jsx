import { useEffect } from 'react';

const upsertMeta = (selector, attributes, content) => {
  let element = document.head.querySelector(selector);
  if (!element) {
    element = document.createElement('meta');
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    document.head.appendChild(element);
  }
  element.setAttribute('content', content);
};

export default function PageMetadata({ title, description, noIndex = false, jsonLd }) {
  useEffect(() => {
    const siteOrigin = (import.meta.env.VITE_PUBLIC_SITE_URL || window.location.origin).replace(/\/$/, '');
    const path = window.location.pathname || '/';
    const canonicalUrl = `${siteOrigin}${path}`;
    const fullTitle = title ? `${title} | FreightDoc` : 'FreightDoc | Global trade documentation workspace';
    document.title = fullTitle;
    upsertMeta('meta[name="description"]', { name: 'description' }, description);
    upsertMeta('meta[name="robots"]', { name: 'robots' }, noIndex ? 'noindex, nofollow' : 'index, follow, max-image-preview:large');
    upsertMeta('meta[property="og:title"]', { property: 'og:title' }, fullTitle);
    upsertMeta('meta[property="og:description"]', { property: 'og:description' }, description);
    upsertMeta('meta[property="og:url"]', { property: 'og:url' }, canonicalUrl);
    upsertMeta('meta[name="twitter:title"]', { name: 'twitter:title' }, fullTitle);
    upsertMeta('meta[name="twitter:description"]', { name: 'twitter:description' }, description);

    let canonical = document.head.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', canonicalUrl);

    const schemaId = 'freightdoc-public-schema';
    document.getElementById(schemaId)?.remove();
    if (jsonLd) {
      const schema = document.createElement('script');
      schema.id = schemaId;
      schema.type = 'application/ld+json';
      schema.text = JSON.stringify(jsonLd);
      document.head.appendChild(schema);
    }
  }, [title, description, noIndex, jsonLd]);

  return null;
}
