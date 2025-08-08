import { render } from '@testing-library/svelte';
import CommunityPostPage from '../../../src/routes/community/[postId]/+page.svelte';
import type { User } from '../../../src/lib/types.js';

interface Post {
  id: string;
  title: string;
  content: string;
  author: User;
  createdAt: string;
  comments: any[];
}

const mockPost: Post = {
  id: '1',
  title: '测试帖子',
  content: '这是测试帖子内容',
  author: { id: '1', name: '测试用户' },
  createdAt: '2025-01-01',
  comments: []
};

interface PageData {
  postId: string;
}

describe('Community Post Page', () => {
  it('shows post not found by default', async () => {
    const { getByText } = render(CommunityPostPage, {
      props: { data: { postId: '1' } as PageData }
    });
    expect(getByText('帖子不存在')).toBeInTheDocument();
  });

  // 由于组件内部使用store管理状态，无法通过props直接测试
  // 需要重构组件才能完整测试其他状态
  // 当前只测试默认状态
});
