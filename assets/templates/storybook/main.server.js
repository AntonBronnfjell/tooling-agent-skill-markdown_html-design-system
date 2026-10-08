// Storybook (server renderer) — created by `ds.py storybook --renderer server`; safe to edit (only --force overwrites it).
// Stories are JSON; each one asks a backend for its HTML: GET {server.url}/{story id}?{args}.
// Default backend: `ds.py serve .` (renders the reference markup from the component pages). Point STORYBOOK_SERVER_URL
// at Laravel/Django/Rails/Spring/ASP.NET to render your own templates — see references/storybook.md §4.
import { existsSync } from 'node:fs';

/** @type {import('@storybook/server-webpack5').StorybookConfig} */
export default {
  framework: '@storybook/server-webpack5',
  stories: ['../stories/**/*.mdx', '../stories/**/*.stories.json'],
  addons: ['@storybook/addon-docs', '@storybook/addon-a11y'],
  core: { disableTelemetry: true },
  // The system's CSS is linked from preview-head.html; the backend returns fragments only.
  staticDirs: [{ from: '../dist', to: '/ds/dist' }, { from: '../docs', to: '/ds/docs' },
    ...(existsSync('fonts') ? [{ from: '../fonts', to: '/fonts' }] : [])],
};
