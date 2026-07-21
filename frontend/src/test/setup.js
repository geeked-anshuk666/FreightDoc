import '@testing-library/jest-dom/vitest';

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query) => ({
    matches: query.includes('min-width') ? true : false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

window.requestAnimationFrame ||= (callback) => window.setTimeout(callback, 0);
window.cancelAnimationFrame ||= (id) => window.clearTimeout(id);
Element.prototype.scrollIntoView ||= () => {};
URL.createObjectURL ||= () => 'blob:freightdoc-test';
URL.revokeObjectURL ||= () => {};
HTMLMediaElement.prototype.play = () => Promise.resolve();
HTMLMediaElement.prototype.pause = () => {};
