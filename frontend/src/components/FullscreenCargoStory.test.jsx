import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const timeline = { addLabel: vi.fn().mockReturnThis(), set: vi.fn().mockReturnThis(), to: vi.fn().mockReturnThis(), kill: vi.fn() };
const media = { add: vi.fn(() => undefined), revert: vi.fn() };
vi.mock('gsap', () => ({
  gsap: {
    registerPlugin: vi.fn(),
    context: (callback) => { callback(); return { revert: vi.fn() }; },
    matchMedia: () => media,
    timeline: () => timeline,
  },
}));
vi.mock('gsap/ScrollTrigger', () => ({ ScrollTrigger: {} }));

import FullscreenCargoStory from './FullscreenCargoStory';

describe('FullscreenCargoStory', () => {
  beforeEach(() => {
    media.add.mockClear();
    timeline.addLabel.mockClear();
    timeline.set.mockClear();
  });

  it('keeps the hero content and cargo fleet present for mobile layouts', () => {
    render(<FullscreenCargoStory><h1>Move trade with certainty.</h1></FullscreenCargoStory>);
    expect(screen.getByRole('heading', { name: 'Move trade with certainty.' })).toBeInTheDocument();
    expect(document.querySelectorAll('.cargo-story__container')).toHaveLength(7);
    expect(screen.getByText('SCROLL TO LOAD')).toBeInTheDocument();
  });

  it('registers responsive motion media queries and can clean up on unmount', () => {
    const { unmount } = render(<FullscreenCargoStory><p>Hero</p></FullscreenCargoStory>);
    expect(media.add).toHaveBeenCalledWith(expect.objectContaining({ mobile: '(max-width: 760px)', reduceMotion: '(prefers-reduced-motion: reduce)' }), expect.any(Function));
    unmount();
  });
});
