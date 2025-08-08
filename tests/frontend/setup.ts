import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// Enhanced SvelteKit mocks
vi.mock('$app/stores', () => ({
  page: {
    subscribe: (fn: any) => {
      fn({ data: {} });
      return () => {};
    }
  },
  navigating: {
    subscribe: (fn: any) => {
      fn(null);
      return () => {};
    }
  },
  updated: {
    subscribe: (fn: any) => {
      fn(false);
      return () => {};
    }
  }
}));

vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
  invalidate: vi.fn()
}));

// 配置测试库以正确处理SvelteKit页面组件
vi.mock('../../../src/routes/cats/+page.svelte', () => ({
  default: {
    render: (options: any) => ({
      $$typeof: Symbol.for('svelte.component'),
      $capture_state: () => ({}),
      $inject_state: () => ({}),
      render: (options: any) => ({})
    })
  }
}));
