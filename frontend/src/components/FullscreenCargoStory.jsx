import { useEffect, useRef } from 'react';
import './fullscreen-cargo-story.css';

const clamp = (value) => Math.max(0, Math.min(1, value));
const smooth = (value) => value * value * (3 - 2 * value);
const between = (progress, start, end) => smooth(clamp((progress - start) / (end - start)));

const cargo = [
  { id: 'scarlet', tone: 'scarlet', x: '-11vw', y: '-16vh', r: '-9deg', enter: [0.16, 0.56], end: ['-7vw', '21vh', '0deg'] },
  { id: 'ocean', tone: 'ocean', x: '31vw', y: '-3vh', r: '7deg', enter: [0.24, 0.63], end: ['7vw', '24vh', '0deg'] },
  { id: 'gold', tone: 'gold', x: '13vw', y: '-24vh', r: '-4deg', enter: [0.32, 0.71], end: ['0vw', '9vh', '0deg'] },
  { id: 'jade', tone: 'jade', x: '50vw', y: '18vh', r: '11deg', enter: [0.37, 0.77], end: ['15vw', '9vh', '0deg'] },
  { id: 'navy', tone: 'navy', x: '-35vw', y: '21vh', r: '-14deg', enter: [0.42, 0.81], end: ['-15vw', '9vh', '0deg'] },
  { id: 'rust', tone: 'rust', x: '5vw', y: '34vh', r: '5deg', enter: [0.47, 0.85], end: ['-7vw', '-6vh', '0deg'] },
  { id: 'slate', tone: 'slate', x: '43vw', y: '-25vh', r: '-8deg', enter: [0.5, 0.88], end: ['7vw', '-6vh', '0deg'] },
];

function Container({ item }) {
  return <div className={`cargo-unit cargo-${item.tone}`} data-cargo={item.id} style={{ '--x': item.x, '--y': item.y, '--r': item.r }}>
    <i className="cargo-side" /><i className="cargo-door" /><i className="cargo-ribs" /><i className="cargo-spreader" /><i className="cargo-cable cable-left" /><i className="cargo-cable cable-right" />
  </div>;
}

export default function FullscreenCargoStory({ children }) {
  const rootRef = useRef(null);
  const stageRef = useRef(null);
  const copyRef = useRef(null);
  const arrivalRef = useRef(null);
  const fleetRef = useRef(null);

  useEffect(() => {
    const root = rootRef.current;
    const stage = stageRef.current;
    if (!root || !stage) return undefined;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let frame = 0;
    const update = () => {
      const rect = root.getBoundingClientRect();
      const progress = reduced ? 0.9 : clamp(-rect.top / Math.max(1, rect.height - window.innerHeight));
      stage.style.setProperty('--story-progress', progress.toFixed(4));
      stage.style.setProperty('--copy-out', between(progress, 0.12, 0.28).toFixed(4));
      stage.style.setProperty('--arrival', between(progress, 0.78, 0.94).toFixed(4));
      stage.style.setProperty('--terminal-shift', `${(-progress * 8).toFixed(2)}vh`);
      stage.style.setProperty('--vessel-scale', (0.78 + between(progress, 0.48, 0.82) * 0.25).toFixed(3));
      fleetRef.current?.querySelectorAll('[data-cargo]').forEach((element) => {
        const item = cargo.find((entry) => entry.id === element.dataset.cargo);
        const t = between(progress, item.enter[0], item.enter[1]);
        const landing = between(progress, item.enter[1], Math.min(0.92, item.enter[1] + 0.12));
        const [endX, endY, endR] = item.end;
        const px = (value, axis) => (parseFloat(value) / 100) * (axis === 'x' ? window.innerWidth : window.innerHeight);
        const startX = px(item.x, 'x'); const startY = px(item.y, 'y'); const finishX = px(endX, 'x'); const finishY = px(endY, 'y');
        const startR = parseFloat(item.r); const finishR = parseFloat(endR);
        element.style.setProperty('--move', t.toFixed(4));
        element.style.setProperty('--settle', landing.toFixed(4));
        element.style.setProperty('--current-x', `${startX + (finishX - startX) * t}px`);
        element.style.setProperty('--current-y', `${startY + (finishY - startY) * t}px`);
        element.style.setProperty('--current-r', `${startR + (finishR - startR) * t}deg`);
        element.style.setProperty('--current-scale', (1 + t * .2 - landing * .18).toFixed(3));
      });
      copyRef.current?.style.setProperty('--copy-out', between(progress, 0.1, 0.26).toFixed(4));
      arrivalRef.current?.style.setProperty('--arrival', between(progress, 0.78, 0.94).toFixed(4));
      frame = 0;
    };
    const request = () => { if (!frame) frame = requestAnimationFrame(update); };
    update(); window.addEventListener('scroll', request, { passive: true }); window.addEventListener('resize', request);
    return () => { window.removeEventListener('scroll', request); window.removeEventListener('resize', request); cancelAnimationFrame(frame); };
  }, []);

  return <section id="top" className="logistics-story" ref={rootRef}>
    <div className="logistics-stage" ref={stageRef}>
      <div className="terminal-sky" /><div className="terminal-haze" /><div className="terminal-grid" />
      <div className="port-line port-far"><i /><i /><i /><i /><i /></div>
      <div className="gantry gantry-left"><i className="gantry-post" /><i className="gantry-beam" /><i className="gantry-leg first" /><i className="gantry-leg second" /></div>
      <div className="gantry gantry-right"><i className="gantry-post" /><i className="gantry-beam" /><i className="gantry-leg first" /><i className="gantry-leg second" /></div>
      <div className="story-wordmark">FREIGHTDOC</div>
      <div className="cargo-fleet" ref={fleetRef}>{cargo.map((item) => <Container key={item.id} item={item} />)}</div>
      <div className="vessel"><div className="vessel-bridge" /><div className="vessel-deck"><b /><b /><b /><b /></div><div className="vessel-hull" /></div>
      <div className="logistics-vignette" />
      <div ref={copyRef} className="story-copy">{children}</div>
      <div ref={arrivalRef} className="story-arrival"><span>FREIGHTDOC / SHIPMENT PREPARATION</span><strong>From brief to berth.</strong><small>Your shipment workspace is ready below.</small></div>
      <div className="story-progress" aria-hidden="true"><span>SCROLL TO LOAD</span><i /></div>
    </div>
  </section>;
}
