import { render as svelteRender } from '@testing-library/svelte';
import { tick } from 'svelte';

export async function renderPageComponent(component: any, options: any = {}) {
  // 处理SvelteKit页面组件
  if (component?.default) {
    component = component.default;
  }

  // 对于SvelteKit页面组件，直接渲染组件类
  if (typeof component === 'object' && component.render) {
    const result = svelteRender(component, options.props || {});
    await tick();
    return result;
  }

  // 确保组件是可渲染的
  if (typeof component !== 'function' && !component.$$typeof) {
    throw new Error('Component must be a constructor function or Svelte component');
  }

  // 直接渲染组件
  const result = svelteRender(component, options.props || {});
  await tick();
  return result;
}
