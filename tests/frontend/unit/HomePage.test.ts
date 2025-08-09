import { render } from '@testing-library/svelte';
import '@testing-library/jest-dom';
import HomePage from '../../../src/routes/+page.svelte';
import { authStore } from '$lib/stores/auth.store.ts';
import type { Mock } from 'vitest';

describe('HomePage Component', () => {
  it('renders welcome message', () => {
    const { getByText } = render(HomePage);
    expect(getByText('欢迎来到CATalogue')).toBeInTheDocument();
    expect(getByText('专业的猫咪档案管理与社区平台')).toBeInTheDocument();
  });

  it('shows login buttons by default', () => {
    const { getByText } = render(HomePage);
    expect(getByText('登录')).toBeInTheDocument();
    expect(getByText('注册')).toBeInTheDocument();
  });

  it('shows app buttons when authenticated', async () => {
    const mockAuthState = { 
      isAuthenticated: true, 
      user: { username: 'test', email: 'test@example.com' } 
    };
    
    (authStore.subscribe as Mock).mockImplementation((fn) => {
      fn(mockAuthState);
      return () => {};
    });

    const { getByText } = render(HomePage);
    await new Promise(resolve => setTimeout(resolve, 100)); // Longer wait for Svelte reactivity
    expect(getByText('查看猫咪档案')).toBeInTheDocument();
    expect(getByText('进入社区')).toBeInTheDocument();
  });
});
