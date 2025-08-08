import { RenderResult } from '@testing-library/svelte';
import type { SvelteComponent } from 'svelte';

export function renderPageComponent(
  component: typeof SvelteComponent | 
           { default: typeof SvelteComponent } | 
           { render?: any, $$typeof?: symbol } |
           { [key: string]: any } |
           any,
  options?: any
): Promise<RenderResult<any>>;

// 添加Wrapper组件类型声明
declare class Wrapper extends SvelteComponent {
  constructor(options: any);
  $$typeof: symbol;
}
