import { useState } from 'react';
export default function DownloadBar({ pdfs = {} }) {
  const [state, setState] = useState('idle');
  const [message, setMessage] = useState('');

  const download = async () => {
    if (!Object.keys(pdfs).length) {
      setState('error');
      setMessage('The PDF package is not available yet. Regenerate the dossier.');
      return;
    }

    try {
      setState('loading');
      // Keep the sizeable ZIP implementation out of the initial workspace bundle.
      const module = await import('jszip');
      const Zip = module.default || module;
      const zip = new Zip();
      Object.entries(pdfs).forEach(([name, base64]) => {
        zip.file(`${name.replace(/\.pdf$/i, '')}.pdf`, base64, { base64: true });
      });
      const blob = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'freightdoc-complete-dossier.zip';
      link.setAttribute('aria-label', 'Download complete dossier package as a ZIP file');
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Some browsers resolve the click asynchronously; defer cleanup to avoid a
      // zero-byte download while still releasing the object URL promptly.
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setState('success');
      setMessage('Complete dossier download started.');
    } catch {
      setState('error');
      setMessage('We could not prepare the dossier download. Please try again.');
    }
  };

  return <div className="download-bar">
    <div role={state === 'error' ? 'alert' : 'status'} aria-live="polite" aria-atomic="true">
      <b>{state === 'success' ? 'Dossier ready' : 'Complete document package'}</b>
      <span>{message || 'Generated PDFs are bundled into one ZIP download.'}</span>
    </div>
    <button className="download" type="button" disabled={state === 'loading'} aria-busy={state === 'loading'} onClick={download}>
      {state === 'loading' ? 'Preparing download…' : 'Download dossier package (.zip)'}
    </button>
  </div>;
}
