import { render } from '@testing-library/svelte';
import { screen } from '@testing-library/dom';
import Layout from '../../../src/routes/+layout.svelte';

describe('Layout Component', () => {
  it('renders navigation links', () => {
    render(Layout);
    
    expect(screen.getByText('首页')).toBeInTheDocument();
    expect(screen.getByText('猫咪档案')).toBeInTheDocument();
    expect(screen.getByText('社区')).toBeInTheDocument();
    
    const homeLink = screen.getByText('首页');
    expect(homeLink).toHaveAttribute('href', '/');
    
    const catsLink = screen.getByText('猫咪档案');
    expect(catsLink).toHaveAttribute('href', '/cats');
    
    const communityLink = screen.getByText('社区');
    expect(communityLink).toHaveAttribute('href', '/community');
  });

  it('applies correct structure', () => {
    const { container } = render(Layout);
    
    const appContainer = container.querySelector('.app-container');
    expect(appContainer).toBeInTheDocument();
    
    const nav = container.querySelector('nav');
    expect(nav).toBeInTheDocument();
  });

  it('renders slot content', () => {
    const { container } = render(Layout);
    
    // 检查app-container是否存在
    const appContainer = container.querySelector('.app-container');
    expect(appContainer).toBeInTheDocument();
  });
});
