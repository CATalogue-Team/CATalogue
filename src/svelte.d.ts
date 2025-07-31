/// <reference types="@sveltejs/kit" />

declare module '*.svelte' {
  import { SvelteComponent } from 'svelte';
  export default class extends SvelteComponent {}
}

declare module '$lib/components/*.svelte' {
  import { SvelteComponent } from 'svelte';
  export default class extends SvelteComponent {}
}

declare module '@testing-library/svelte' {
  import { SvelteComponent } from 'svelte';
  export function render<T extends SvelteComponent>(
    component: new (...args: any) => T,
    options?: {
      props?: T extends SvelteComponent<infer Props> ? Props : never;
      target?: HTMLElement;
    }
  ): {
    container: HTMLElement;
    component: T;
    [key: string]: any;
  };
}

declare global {
  namespace svelte.JSX {
    interface HTMLAttributes<T> {
      onclick_outside?: (e: CustomEvent) => void;
    }
  }
}
