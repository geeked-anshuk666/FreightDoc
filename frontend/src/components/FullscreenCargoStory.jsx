import { useLayoutEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import './fullscreen-cargo-story.css';
import './fullscreen-cargo-story-overrides.css';

gsap.registerPlugin(ScrollTrigger);

const CARGO_UNITS = [
  { id: 'front-left', tone: 'vermilion', className: 'is-front-left', mark: 'FDC 014' },
  { id: 'front-right', tone: 'marine', className: 'is-front-right', mark: 'FDC 028' },
  { id: 'suspended', tone: 'amber', className: 'is-suspended', mark: 'FDC 091', suspended: true },
  { id: 'lateral', tone: 'jade', className: 'is-lateral', mark: 'FDC 076' },
  { id: 'mid-left', tone: 'slate', className: 'is-mid-left', mark: 'FDC 103' },
  { id: 'mid-centre', tone: 'coral', className: 'is-mid-centre', mark: 'FDC 042' },
  { id: 'far-right', tone: 'ocean', className: 'is-far-right', mark: 'FDC 118' },
];

function CargoUnit({ unit, register }) {
  return (
    <div
      ref={register(unit.id)}
      className={`cargo-story__container cargo-story__container--${unit.tone} ${unit.className}`}
      aria-hidden="true"
    >
      {unit.suspended && <><span className="cargo-story__cable cargo-story__cable--left" /><span className="cargo-story__cable cargo-story__cable--right" /><span className="cargo-story__spreader" /></>}
      <span className="cargo-story__container-top" />
      <span className="cargo-story__container-face">
        <b>{unit.mark}</b>
        <i />
      </span>
      <span className="cargo-story__container-side" />
    </div>
  );
}

export default function FullscreenCargoStory({ children }) {
  const rootRef = useRef(null);
  const sceneRef = useRef({});

  const register = (name) => (node) => {
    sceneRef.current[name] = node;
  };

  useLayoutEffect(() => {
    const root = rootRef.current;
    if (!root) return undefined;

    const context = gsap.context(() => {
      const media = gsap.matchMedia();
      const scene = sceneRef.current;
      const get = (...names) => names.map((name) => scene[name]).filter(Boolean);

      media.add(
        {
          desktop: '(min-width: 1101px)',
          tablet: '(min-width: 761px) and (max-width: 1100px)',
          mobile: '(max-width: 760px)',
          reduceMotion: '(prefers-reduced-motion: reduce)',
        },
        (mediaContext) => {
          const { reduceMotion } = mediaContext.conditions;

          // CSS owns the reduced-motion composition. It intentionally has no pin or scroll trigger.
          if (reduceMotion) return undefined;

          const timeline = gsap.timeline({
            defaults: { duration: 1, ease: 'none' },
            scrollTrigger: {
              id: 'freightdoc-cargo-story',
              trigger: root,
              start: 'top top',
              end: 'bottom bottom',
              pin: scene.stage,
              pinSpacing: false,
              scrub: 0.75,
              anticipatePin: 1,
              invalidateOnRefresh: true,
            },
          });

          const intro = scene.intro;
          const manifest = scene.manifest;
          const handoff = scene.handoff;
          const progress = scene.progress;

          timeline
            .addLabel('beat-0-opening', 0)
            .set(get('manifest', 'handoff'), { autoAlpha: 0 }, 'beat-0-opening')
            .set(scene.suspended, { y: '-31vh', rotation: -5, rotationY: -8, scale: 0.88 }, 'beat-0-opening')
            .set(scene.lateral, { rotation: 4, rotationY: -10 }, 'beat-0-opening')
            .set(scene['front-left'], { rotation: -6, rotationY: 8, scale: 1.04 }, 'beat-0-opening')
            .set(scene['front-right'], { rotation: 6, rotationY: -9, scale: 1.02 }, 'beat-0-opening')
            .set(progress, { scaleX: 0.08, transformOrigin: 'left center' }, 'beat-0-opening')

            .addLabel('beat-25-approach', 1)
            .to(scene.sky, { yPercent: -4, scale: 1.045 }, 'beat-0-opening')
            .to(scene.haze, { yPercent: -9, scale: 1.08 }, 'beat-0-opening')
            .to(scene.horizon, { x: '-2vw', y: '1.5vh', scale: 0.98 }, 'beat-0-opening')
            .to(scene['crane-far'], { x: '-4vw', y: '1vh' }, 'beat-0-opening')
            .to(scene['crane-near'], { x: '5vw', y: '-1vh' }, 'beat-0-opening')
            .to(scene.wordmark, { x: '-10vw', y: '-2vh', scale: 1.06, autoAlpha: 0.42 }, 'beat-0-opening')
            .to(scene.vessel, { x: '-2vw', y: '1vh', scale: 1.025 }, 'beat-0-opening')
            .to(scene.suspended, { y: '8vh', rotation: -1, rotationY: 2, scale: 1 }, 'beat-0-opening')
            .to(scene.lateral, { x: '-13vw', y: '-5vh', rotation: -1, rotationY: -2, scale: 1.04 }, 'beat-0-opening')
            .to(scene['front-left'], { x: '-7vw', y: '5vh', rotation: -9, scale: 1.12 }, 'beat-0-opening')
            .to(scene['front-right'], { x: '7vw', y: '-7vh', rotation: 3, scale: 1.11 }, 'beat-0-opening')
            .to(scene['mid-left'], { x: '-3vw', y: '-2vh', rotation: -3, scale: 1.05 }, 'beat-0-opening')
            .to(intro, { y: -46, autoAlpha: 0 }, 'beat-25-approach-=0.72')
            .to(progress, { scaleX: 0.31 }, 'beat-0-opening')

            .addLabel('beat-50-transfer', 2)
            .to(scene.sky, { yPercent: -7, scale: 1.08 }, 'beat-25-approach')
            .to(scene.horizon, { x: '-5vw', y: '3vh', scale: 0.95 }, 'beat-25-approach')
            .to(scene['crane-far'], { x: '-8vw', y: '2vh' }, 'beat-25-approach')
            .to(scene['crane-near'], { x: '9vw', y: '-2vh' }, 'beat-25-approach')
            .to(scene.wordmark, { x: '-17vw', y: '-5vh', scale: 1.13, autoAlpha: 0.18 }, 'beat-25-approach')
            .to(scene.vessel, { x: '-6vw', y: '2vh', scale: 1.065 }, 'beat-25-approach')
            .to(scene.suspended, { x: '-11vw', y: '23vh', rotation: 1, rotationY: 5, scale: 0.96 }, 'beat-25-approach')
            .to(scene.lateral, { x: '-37vw', y: '4vh', rotation: -5, rotationY: 8, scale: 1.13 }, 'beat-25-approach')
            .to(scene['front-left'], { x: '-16vw', y: '10vh', rotation: -12, scale: 1.22 }, 'beat-25-approach')
            .to(scene['front-right'], { x: '14vw', y: '-11vh', rotation: 1, scale: 1.2 }, 'beat-25-approach')
            .to(scene['mid-left'], { x: '8vw', y: '4vh', rotation: 1, scale: 1.1 }, 'beat-25-approach')
            .to(scene['mid-centre'], { x: '-8vw', y: '-9vh', rotation: -3, scale: 1.1 }, 'beat-25-approach')
            .to(scene['far-right'], { x: '-15vw', y: '5vh', rotation: -2, scale: 1.08 }, 'beat-25-approach')
            .to(manifest, { y: 0, autoAlpha: 1 }, 'beat-50-transfer-=0.7')
            .to(progress, { scaleX: 0.55 }, 'beat-25-approach')

            .addLabel('beat-75-organise', 3)
            .to(scene.sky, { yPercent: -10, scale: 1.11 }, 'beat-50-transfer')
            .to(scene.haze, { yPercent: -14, scale: 1.12 }, 'beat-50-transfer')
            .to(scene.horizon, { x: '-7vw', y: '4vh', scale: 0.93 }, 'beat-50-transfer')
            .to(scene.wordmark, { x: '-23vw', y: '-7vh', scale: 1.18, autoAlpha: 0.12 }, 'beat-50-transfer')
            .to(scene.vessel, { x: '-9vw', y: '3vh', scale: 1.1 }, 'beat-50-transfer')
            .to(scene.suspended, { x: '-20vw', y: '31vh', rotation: 0, rotationY: 0, scale: 0.84 }, 'beat-50-transfer')
            .to(scene.lateral, { x: '-49vw', y: '16vh', rotation: -2, rotationY: 0, scale: 0.92 }, 'beat-50-transfer')
            .to(scene['front-left'], { x: '-30vw', y: '17vh', rotation: -8, scale: 1.04 }, 'beat-50-transfer')
            .to(scene['front-right'], { x: '29vw', y: '5vh', rotation: 4, scale: 1.02 }, 'beat-50-transfer')
            .to(scene['mid-left'], { x: '-2vw', y: '17vh', rotation: 0, scale: 0.93 }, 'beat-50-transfer')
            .to(scene['mid-centre'], { x: '3vw', y: '12vh', rotation: 0, scale: 0.9 }, 'beat-50-transfer')
            .to(scene['far-right'], { x: '9vw', y: '15vh', rotation: 0, scale: 0.85 }, 'beat-50-transfer')
            .to(manifest, { y: -34, autoAlpha: 0 }, 'beat-75-organise-=0.64')
            .to(handoff, { y: 0, autoAlpha: 1 }, 'beat-75-organise-=0.42')
            .to(progress, { scaleX: 0.79 }, 'beat-50-transfer')

            .addLabel('beat-100-arrival', 4)
            .to(scene.sky, { yPercent: -12, scale: 1.13 }, 'beat-75-organise')
            .to(scene.horizon, { x: '-9vw', y: '5vh', scale: 0.91 }, 'beat-75-organise')
            .to(scene['crane-far'], { x: '-11vw', y: '3vh' }, 'beat-75-organise')
            .to(scene['crane-near'], { x: '12vw', y: '-3vh' }, 'beat-75-organise')
            .to(scene.wordmark, { x: '-28vw', y: '-9vh', scale: 1.23, autoAlpha: 0.1 }, 'beat-75-organise')
            .to(scene.vessel, { x: '-12vw', y: '4vh', scale: 1.13 }, 'beat-75-organise')
            .to(scene.suspended, { x: '-24vw', y: '34vh', scale: 0.79 }, 'beat-75-organise')
            .to(scene.lateral, { x: '-55vw', y: '19vh', scale: 0.86 }, 'beat-75-organise')
            .to(scene['front-left'], { x: '-37vw', y: '21vh', rotation: -5, scale: 0.94 }, 'beat-75-organise')
            .to(scene['front-right'], { x: '37vw', y: '9vh', rotation: 4, scale: 0.93 }, 'beat-75-organise')
            .to(scene['mid-left'], { x: '-7vw', y: '21vh', scale: 0.86 }, 'beat-75-organise')
            .to(scene['mid-centre'], { x: '5vw', y: '17vh', scale: 0.84 }, 'beat-75-organise')
            .to(scene['far-right'], { x: '14vw', y: '19vh', scale: 0.8 }, 'beat-75-organise')
            .to(progress, { scaleX: 1 }, 'beat-75-organise');

          return () => timeline.kill();
        },
      );

      return () => media.revert();
    }, root);

    return () => context.revert();
  }, []);

  return (
    <section id="top" className="cargo-story" ref={rootRef}>
      <div className="cargo-story__stage" ref={register('stage')}>
        <div className="cargo-story__sky" ref={register('sky')} aria-hidden="true">
          <span className="cargo-story__sun" />
          <span className="cargo-story__cloud cargo-story__cloud--one" />
          <span className="cargo-story__cloud cargo-story__cloud--two" />
        </div>
        <div className="cargo-story__haze" ref={register('haze')} aria-hidden="true" />
        <div className="cargo-story__coordinates" aria-hidden="true" />
        <div className="cargo-story__wordmark" ref={register('wordmark')} aria-hidden="true">FREIGHTDOC</div>

        <div className="cargo-story__horizon" ref={register('horizon')} aria-hidden="true">
          <div className="cargo-story__terminal-line" />
          <div className="cargo-story__water" />
        </div>

        <div className="cargo-story__crane cargo-story__crane--far" ref={register('crane-far')} aria-hidden="true">
          <span className="cargo-story__crane-mast" /><span className="cargo-story__crane-boom" /><span className="cargo-story__crane-brace cargo-story__crane-brace--one" /><span className="cargo-story__crane-brace cargo-story__crane-brace--two" />
        </div>
        <div className="cargo-story__crane cargo-story__crane--near" ref={register('crane-near')} aria-hidden="true">
          <span className="cargo-story__crane-mast" /><span className="cargo-story__crane-boom" /><span className="cargo-story__crane-brace cargo-story__crane-brace--one" /><span className="cargo-story__crane-brace cargo-story__crane-brace--two" />
        </div>

        <div className="cargo-story__vessel-anchor" aria-hidden="true"><div className="cargo-story__vessel" ref={register('vessel')}><span className="cargo-story__vessel-bridge" /><span className="cargo-story__vessel-stack cargo-story__vessel-stack--one" /><span className="cargo-story__vessel-stack cargo-story__vessel-stack--two" /><span className="cargo-story__vessel-stack cargo-story__vessel-stack--three" /><span className="cargo-story__vessel-hull" /></div></div>

        <div className="cargo-story__fleet">
          {CARGO_UNITS.map((unit) => <CargoUnit key={unit.id} unit={unit} register={register} />)}
        </div>

        <div className="cargo-story__vignette" aria-hidden="true" />

        <div className="cargo-story__intro" ref={register('intro')}>
          {children}
        </div>
        <div className="cargo-story__manifest" ref={register('manifest')} aria-hidden="true">
          <span>PORT OF DEPARTURE / READY FOR REVIEW</span>
          <strong>Clarity in motion.</strong>
          <small>Route, tariff logic, and document checks move as one load.</small>
        </div>
        <div className="cargo-story__handoff" ref={register('handoff')} aria-hidden="true">
          <span>FREIGHTDOC / SHIPMENT PREPARATION</span>
          <strong>From brief to berth.</strong>
          <small>Your shipment workspace follows this scene.</small>
        </div>

        <div className="cargo-story__scrollcue" aria-hidden="true"><span>SCROLL TO LOAD</span><i ref={register('progress')} /></div>
      </div>
    </section>
  );
}
