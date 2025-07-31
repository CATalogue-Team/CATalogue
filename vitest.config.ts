import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({
    compilerOptions: {
      dev: true
    }
  })],
  test: {
    globals: true,
    environment: 'jsdom',
  setupFiles: ['./tests/shared/utils/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
    deps: {
      inline: [
        '@sveltejs/vite-plugin-svelte',
        '@testing-library/svelte',
        '@sveltejs/kit'
      ]
    },
    server: {
      deps: {
        inline: [
          '@testing-library/svelte', 
          '@sveltejs/kit',
          '@testing-library/jest-dom'
        ]
      }
    }
  }
});
