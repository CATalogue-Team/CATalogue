import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/svelte';
import * as matchers from '@testing-library/jest-dom/matchers';
import '@testing-library/jest-dom/vitest';

// 添加Jest DOM匹配器
expect.extend(matchers);

// 每次测试后清理
afterEach(() => {
  cleanup();
});
