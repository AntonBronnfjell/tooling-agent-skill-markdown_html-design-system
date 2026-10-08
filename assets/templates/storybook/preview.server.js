// Created by `ds.py storybook --renderer server`; safe to edit (only --force overwrites it).
import { addons } from 'storybook/preview-api';
import { themes } from '../stories/_meta.js';

const root = document.documentElement;

/** Same toolbar contract as every other workbench: attributes on <html>, like production. */
function apply(globals = {}) {
  globals.theme && globals.theme !== 'system' ? root.setAttribute('data-theme', globals.theme) : root.removeAttribute('data-theme');
  globals.density === 'compact' ? root.setAttribute('data-density', 'compact') : root.removeAttribute('data-density');
  root.dir = globals.dir || 'ltr';
  root.toggleAttribute('data-reduced-motion', globals.motion === 'reduced');
}
// Server-rendered stories have no JS decorators, so follow the globals over the channel instead.
const channel = addons.getChannel();
channel.on('setGlobals', ({ globals }) => apply(globals));
channel.on('globalsUpdated', ({ globals }) => apply(globals));

export default {
  globalTypes: {
    theme: { description: 'Theme', toolbar: { title: 'Theme', icon: 'paintbrush', items: ['system', ...themes], dynamicTitle: true } },
    density: { description: 'Density', toolbar: { title: 'Density', icon: 'component', items: ['comfortable', 'compact'], dynamicTitle: true } },
    dir: { description: 'Text direction', toolbar: { title: 'Direction', icon: 'transfer', items: ['ltr', 'rtl'], dynamicTitle: true } },
    motion: { description: 'Motion', toolbar: { title: 'Motion', icon: 'lightning', items: ['full', 'reduced'], dynamicTitle: true } },
  },
  initialGlobals: { theme: 'system', density: 'comfortable', dir: 'ltr', motion: 'full' },
  parameters: {
    server: { url: process.env.STORYBOOK_SERVER_URL || '__SERVER_URL__' },
    layout: 'padded',
    a11y: { test: 'error' },
    docs: { toc: true },
    options: { storySort: { order: ['Introduction', 'Foundations', 'Actions', 'Forms', 'Navigation', 'Data Display', 'Overlays', 'Feedback', 'Patterns'] } },
  },
};
