// Created by `ds.py storybook`; safe to edit (only --force overwrites it).
import '../dist/ds.css';
import '../docs/docs.css'; // demo layout helpers (.ds-demo__row, .ds-demos)
import { themes } from '../stories/_meta.js';

const root = document.documentElement;

/** Mirror the docs-site toggles: theme, density, direction and motion live on <html>, like in production. */
const withSystemAttributes = (story, { globals }) => {
  globals.theme && globals.theme !== 'system' ? root.setAttribute('data-theme', globals.theme) : root.removeAttribute('data-theme');
  globals.density === 'compact' ? root.setAttribute('data-density', 'compact') : root.removeAttribute('data-density');
  root.dir = globals.dir || 'ltr';
  root.toggleAttribute('data-reduced-motion', globals.motion === 'reduced');
  return story();
};

/** @type {import('@storybook/html-vite').Preview} */
export default {
  tags: ['autodocs'],
  globalTypes: {
    theme: { description: 'Theme', toolbar: { title: 'Theme', icon: 'paintbrush', items: ['system', ...themes], dynamicTitle: true } },
    density: { description: 'Density', toolbar: { title: 'Density', icon: 'component', items: ['comfortable', 'compact'], dynamicTitle: true } },
    dir: { description: 'Text direction', toolbar: { title: 'Direction', icon: 'transfer', items: ['ltr', 'rtl'], dynamicTitle: true } },
    motion: { description: 'Motion', toolbar: { title: 'Motion', icon: 'lightning', items: ['full', 'reduced'], dynamicTitle: true } },
  },
  initialGlobals: { theme: 'system', density: 'comfortable', dir: 'ltr', motion: 'full' },
  decorators: [withSystemAttributes],
  parameters: {
    layout: 'padded',
    a11y: { test: 'error' }, // axe runs on every story; violations fail `storybook test`/CI
    docs: { toc: true },
    options: { storySort: { order: ['Introduction', 'Foundations', 'Actions', 'Forms', 'Navigation', 'Data Display', 'Overlays', 'Feedback', 'Patterns', 'Marketing', 'Marketing Pages'] } },
  },
};
