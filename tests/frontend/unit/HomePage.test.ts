import { render } from '@testing-library/svelte';
import { screen, fireEvent } from '@testing-library/dom';
import { vi } from 'vitest';
import HomePage from '../../../src/routes/+page.svelte';

describe('Home Page', () => {
  beforeEach(() => {
    // Mock SvelteKit navigation
    vi.mock('$app/navigation', () => ({
      goto: vi.fn()
    }));
  });

  it('renders title and description', () => {
    render(HomePage);
    
    expect(screen.getByText('欢迎来到CATalogue')).toBeInTheDocument();
    expect(screen.getByText('猫咪档案管理与社区平台')).toBeInTheDocument();
  });

  it('renders test button', () => {
    render(HomePage);
    
    const button = screen.getByText('转到 GrowthRecord 组件测试页');
    expect(button).toBeInTheDocument();
  });

  it('calls goto on button click', async () => {
    const { component } = render(HomePage);
    const mockGoto = await import('$app/navigation').then(m => m.goto);
    
    const button = screen.getByText('转到 GrowthRecord 组件测试页');
    fireEvent.click(button);
    
    expect(mockGoto).toHaveBeenCalledWith('/temp-test');
  });

  it('applies correct styles', () => {
    const { container } = render(HomePage);
    
    const containerDiv = container.querySelector('.container');
    expect(containerDiv).toBeInTheDocument();
    
    // 检查样式类是否存在
    expect(containerDiv).toHaveClass('container');
    
    const h1 = container.querySelector('h1') as HTMLHeadingElement;
    expect(h1).toBeInTheDocument();
    
    // 检查样式属性是否存在
    expect(getComputedStyle(h1).color).toBeTruthy();
  });
});
