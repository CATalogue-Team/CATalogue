import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import type { SvelteComponent } from 'svelte';

export async function renderPageComponent(
  component: typeof SvelteComponent | { default: typeof SvelteComponent },
  options = {}
) {
  // 处理SvelteKit页面组件
  const Component = component?.default || component;
  
  // 渲染组件
  const result = render(Component, options);
  
  // 等待Svelte完成更新
  await tick();
  
  return result;
}
