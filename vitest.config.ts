import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      $lib: path.resolve('./src/lib')
    }
  },
  plugins: [svelte({
    compilerOptions: {
      dev: true
    },
    extensions: ['.svelte'],
    emitCss: false,
    hot: false
  })],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/shared/utils/setup.ts'],
    server: {
      deps: {
        external: ['@testing-library/svelte/svelte5'],
        inline: [
          '@testing-library/svelte', 
          '@sveltejs/kit',
          '@testing-library/jest-dom'
        ]
      }
    },
    include: ['src/**/*.{test,spec}.{js,ts}', 'tests/frontend/**/*.{test,spec}.{js,ts}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**'],
    },
    deps: {
      inline: [
        '@sveltejs/vite-plugin-svelte',
        '@testing-library/svelte',
        '@sveltejs/kit'
      ]
    }
  }
});
