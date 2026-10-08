// Storybook for the design system. Created by `ds.py storybook`; safe to edit (only --force overwrites it).
// Stories in ../stories are regenerated from the component pages on every `ds.py storybook` run.
import { existsSync } from 'node:fs';

/** @type {import('@storybook/html-vite').StorybookConfig} */
export default {
  framework: '@storybook/html-vite',
  stories: ['../stories/**/*.mdx', '../stories/**/*.stories.js'],
  addons: ['@storybook/addon-docs', '@storybook/addon-a11y'],
  core: { disableTelemetry: true },
  // Self-hosted fonts (see references/packaging.md) are served at the same URL the CSS uses.
  staticDirs: existsSync('fonts') ? [{ from: '../fonts', to: '/fonts' }] : [],
};
