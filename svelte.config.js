import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      fallback: 'index.html'
    }),
    alias: {
      '$lib': 'src/lib',
      '$lib/*': 'src/lib/*'
    },
    prerender: {
      entries: []
    }
  },
  server: {
    port: 5174,
    strictPort: true
  },
  preprocess: vitePreprocess()
};

export default config;
