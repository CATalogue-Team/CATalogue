import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import { get } from 'svelte/store';
import { authStore } from './auth.store.ts';

export interface Post {
  id: string;
  title: string;
  content: string;
  author_id: string;
  created_at: string;
  updated_at: string;
  likes: number;
  comments?: Comment[];
}

export interface Comment {
  id: string;
  content: string;
  author_id: string;
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
      const token = get(authStore).token;
      const response = await fetch(`${baseUrl}/posts`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error(response.statusText);
      const { data } = await response.json();
      const posts = data as Post[];
      update(state => ({ ...state, posts, loading: false }));
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
    }
  }

  async function fetchPost(id: string): Promise<void> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const token = get(authStore).token;
      const response = await fetch(`${baseUrl}/posts/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error(response.statusText);
      const { data } = await response.json();
      const post = data as Post;
      update(state => ({ ...state, currentPost: post, loading: false }));
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      update(state => ({ ...state, error, loading: false }));
    }
  }

  async function createPost(post: Omit<Post, 'id' | 'created_at' | 'updated_at' | 'likes' | 'author_id'>): Promise<boolean> {
    update(state => ({ ...state, loading: true, error: null }));
    try {
      const token = get(authStore).token;
      const response = await fetch(`${baseUrl}/posts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(post)
      });
      if (!response.ok) throw new Error(response.statusText);
      const { data } = await response.json();
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
      const token = get(authStore).token;
      const response = await fetch(`${baseUrl}/posts/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(post)
      });
      if (!response.ok) throw new Error(response.statusText);
      const { data } = await response.json();
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
      const token = get(authStore).token;
      const response = await fetch(`${baseUrl}/posts/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error(response.statusText);
      const { data } = await response.json();
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

  return {
    subscribe,
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    reset: () => set(initialState)
  };
}

export const postStore = createPostStore();
