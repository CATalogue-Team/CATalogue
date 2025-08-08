import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import path from 'path';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [
      './tests/shared/utils/setup.ts',
      './tests/frontend/setup.ts'
    ],
    include: ['src/**/*.{test,spec}.{js,ts}', 'tests/frontend/**/*.{test,spec}.{js,ts}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**'],
    },
    testTimeout: 30000,
    alias: [
      { find: '$app', replacement: path.resolve('./.svelte-kit/runtime/app') },
      { find: '$lib', replacement: path.resolve('./src/lib') },
      { find: /^\$lib\/(.*)/, replacement: path.resolve('./src/lib/$1') }
    ],
    deps: {
      inline: [
        '@sveltejs/kit',
        '@testing-library/svelte',
        'svelte',
        'svelte/internal',
        '$lib'
      ]
    }
  }
});
