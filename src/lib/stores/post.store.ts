import { writable , get , type Writable} from 'svelte/store';
import { authStore, refreshToken } from './auth.store.ts';

export interface Post {
  id: string;
  title: string;
  content: string;
  author_id: string;
  author_name: string;
  created_at: string;
  updated_at: string;
  likes: number;
  comments?: Comment[];
}

export interface Comment {
  id: string;
  content: string;
  author_id: string;
  author_name: string;
  post_id: string;
  created_at: string;
}

export interface PostState {
  posts: Post[];
  currentPost: Post | null;
  loading: boolean;
  error: string | null;
}

const initialState: PostState = {
  posts: [],
  currentPost: null,
  loading: false,
  error: null
};

function createPostStore() {
  const { subscribe, set, update }: Writable<PostState> = writable(initialState);

  const baseUrl = '/api/v1';

  async function fetchPosts(): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const authState = get(authStore);
      if (!authState.token || typeof authState.token !== 'string') throw new Error('未授权，请先登录');
      
      console.log('Current auth state:', authState);
      console.log('Fetching posts with token:', authState.token);
      console.log('Request headers:', {
        'Authorization': `Bearer ${authState.token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      });
      const headers = {
        'Authorization': `Bearer ${authState.token}`.trim(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.log('Final request headers:', headers);
      
      const response = await fetch(`${baseUrl}/posts`, {
        method: 'GET',
        headers,
        credentials: 'include'
      });
      console.log('Request URL:', `${baseUrl}/posts`);
      console.log('Request headers:', {
        'Authorization': `Bearer ${authState.token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      });
      console.log('Response status:', response.status);
      const headersObj: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        headersObj[key] = value;
      });
      console.log('Response headers:', headersObj);
      console.log('Posts API response:', response.status, await response.clone().json()); // 调试日志
      
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await fetchPosts(); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      
      const result = await response.json();
      // 处理不同格式的响应
      const posts = Array.isArray(result.data) ? result.data : 
                   Array.isArray(result) ? result : 
                   [];
      update(state => ({ ...state, posts, loading: false }));
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
    }
  }

  async function fetchPost(id: string): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const { token } = get(authStore);
      if (!token || typeof token !== 'string') throw new Error('未授权，请先登录');
      
      const headers = {
        'Authorization': `Bearer ${token}`.trim(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.log('Final request headers:', headers);
      
      const response = await fetch(`${baseUrl}/posts/${id}`, {
        headers,
        credentials: 'include'
      });
      console.log('Request URL:', `${baseUrl}/posts/${id}`);
      console.log('Request headers:', {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      });
      console.log('Response status:', response.status);
      const headersObj: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        headersObj[key] = value;
      });
      console.log('Response headers:', headersObj);
      
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await fetchPost(id); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      
      const result = await response.json();
      // 处理不同格式的响应
      const post = result.data || result;
      update(state => ({ ...state, currentPost: post, loading: false }));
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
    }
  }

  async function createPost(post: Omit<Post, 'id' | 'created_at' | 'updated_at' | 'likes' | 'author_id'>): Promise<boolean> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const { token } = get(authStore);
      if (!token || typeof token !== 'string') throw new Error('未授权，请先登录');
      
      const headers = {
        'Authorization': `Bearer ${token}`.trim(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.log('Creating post with headers:', headers);
      
      const response = await fetch(`${baseUrl}/posts`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify(post)
      });
      console.log('Create post response:', response.status);
      
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await createPost(post); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      const result = await response.json();
      const data = result.data || result;
      if (!data) throw new Error('No data returned');
      await fetchPosts();
      return true;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
      return false;
    }
  }

  async function updatePost(id: string, post: Partial<Post>): Promise<boolean> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const { token } = get(authStore);
      if (!token || typeof token !== 'string') throw new Error('未授权，请先登录');
      
      const headers = {
        'Authorization': `Bearer ${token}`.trim(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.log('Updating post with headers:', headers);
      
      const response = await fetch(`${baseUrl}/posts/${id}`, {
        method: 'PUT',
        headers,
        credentials: 'include',
        body: JSON.stringify(post)
      });
      console.log('Update post response:', response.status);
      
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await updatePost(id, post); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      const result = await response.json();
      const data = result.data || result;
      if (!data) throw new Error('No data returned');
      await fetchPosts();
      if (get(postStore).currentPost?.id === id) {
        await fetchPost(id);
      }
      return true;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
      return false;
    }
  }

  async function deletePost(id: string): Promise<boolean> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const { token } = get(authStore);
      if (!token || typeof token !== 'string') throw new Error('未授权，请先登录');
      
      const headers = {
        'Authorization': `Bearer ${token}`.trim(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.log('Deleting post with headers:', headers);
      
      const response = await fetch(`${baseUrl}/posts/${id}`, {
        method: 'DELETE',
        headers,
        credentials: 'include'
      });
      console.log('Delete post response:', response.status);
      
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await deletePost(id); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      const result = await response.json();
      const data = result.data || result;
      if (!data) throw new Error('No data returned');
      update(state => ({
        ...state,
        posts: state.posts.filter(p => p.id !== id),
        loading: false
      }));
      return true;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
      return false;
    }
  }

  async function addComment(postId: string, comment: Omit<Comment, 'id' | 'created_at' | 'post_id' | 'author_id'>): Promise<boolean> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const { token, user } = get(authStore);
      if (!token || typeof token !== 'string' || !user?.id) throw new Error('未授权，请先登录');
      
      const response = await fetch(`${baseUrl}/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: JSON.stringify({
          ...comment,
          author_id: user.id
        })
      });
      
      // 处理401错误
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await addComment(postId, comment); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      return true;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
      return false;
    }
  }

  async function deleteComment(postId: string, commentId: string): Promise<boolean> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const { token } = get(authStore);
      if (!token || typeof token !== 'string') throw new Error('未授权，请先登录');
      
      const headers = {
        'Authorization': `Bearer ${token}`.trim(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.log('Deleting comment with headers:', headers);
      
      const response = await fetch(`${baseUrl}/posts/${postId}/comments/${commentId}`, {
        method: 'DELETE',
        headers,
        credentials: 'include'
      });
      console.log('Delete comment response:', response.status);
      
      if (response.status === 401) {
        console.log('Token已过期，尝试刷新');
        const refreshed = await refreshToken();
        if (!refreshed) {
          authStore.update(state => ({ ...state, isAuthenticated: false }));
          localStorage.removeItem('authToken');
          throw new Error('会话已过期，请重新登录');
        }
        return await deleteComment(postId, commentId); // 重试请求
      }
      if (!response.ok) throw new Error(response.statusText);
      return true;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
      return false;
    }
  }

  return {
    subscribe,
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    addComment,
    deleteComment,
    reset: () => set(initialState)
  };
}

export const postStore = createPostStore();
