import { RenderResult } from '@testing-library/svelte';

interface TestRenderOptions {
  props?: Record<string, any>;
  target?: HTMLElement;
  hydrate?: boolean;
}

export function render(
  Component: any,
  options?: TestRenderOptions
): RenderResult;

export async function renderPageComponent(
  component: any,
  options?: TestRenderOptions
): Promise<RenderResult>;
