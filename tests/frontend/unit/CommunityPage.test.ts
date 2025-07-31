import { render } from '@testing-library/svelte';
import CommunityPage from '../../../src/routes/community/+page.svelte';
import type { PageData } from '../../../src/routes/community/+page.svelte';

describe('Community Page', () => {
  it('renders empty state when data is undefined', () => {
    const { getByText } = render(CommunityPage);
    expect(getByText('暂无帖子')).toBeInTheDocument();
  });

  it('renders empty state when no posts', () => {
    const { getByText } = render(CommunityPage, {
      props: {
        data: { posts: [] }
      }
    } as any);
    expect(getByText('暂无帖子')).toBeInTheDocument();
  });

  it('renders post list when posts exist', async () => {
    const mockPosts = [
      {
        id: '1',
        title: 'Test Post',
        author: { name: 'Test User' }
      }
    ];
    
    const { getByText } = render(CommunityPage, {
      props: {
        data: { posts: mockPosts }
      }
    } as any);

    expect(getByText('Test Post')).toBeInTheDocument();
    expect(getByText('作者: Test User')).toBeInTheDocument();
  });
});
