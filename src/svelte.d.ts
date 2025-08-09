/// <reference types="@sveltejs/kit" />

declare module '*.svelte' {
  import { SvelteComponent } from 'svelte';
  export default class extends SvelteComponent {}
}

declare module '$lib/components/*.svelte' {
  import { SvelteComponent } from 'svelte';
  export default class extends SvelteComponent {}
}

declare module '$lib/stores/*' {
  import { Writable } from 'svelte/store';
  
  // Post store types
  interface Post {
    id: string;
    title: string;
    content: string;
    author_id: string;
    created_at: string;
    updated_at: string;
    likes: number;
    comments?: Comment[];
  }

  interface Comment {
    id: string;
    content: string;
    author_id: string;
    post_id: string;
    created_at: string;
  }

  interface PostState {
    posts: Post[];
    currentPost: Post | null;
    loading: boolean;
    error: string | null;
  }

  export const postStore: {
    subscribe: Writable<PostState>['subscribe'];
    fetchPosts: () => Promise<void>;
    fetchPost: (id: string) => Promise<void>;
    createPost: (post: Omit<Post, 'id' | 'created_at' | 'updated_at' | 'likes' | 'author_id'>) => Promise<boolean>;
    updatePost: (id: string, post: Partial<Post>) => Promise<boolean>;
    deletePost: (id: string) => Promise<boolean>;
    reset: () => void;
  };

  // Auth store types
  interface UserInfo {
    username: string;
    email: string;
  }

  interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: UserInfo | null;
  }

  export const authStore: Writable<AuthState>;
  export function login(token: string): void;
  export function logout(): void;
  export function initializeAuth(): Promise<boolean>;
}

declare module '@testing-library/svelte' {
  import { SvelteComponent } from 'svelte';
  export function render<T extends SvelteComponent>(
    component: new (...args: any) => T,
    options?: {
      props?: T extends SvelteComponent<infer Props> ? Props : never;
      target?: HTMLElement;
    }
  ): {
    container: HTMLElement;
    component: T;
    [key: string]: any;
  };
}

declare global {
  namespace svelte.JSX {
    interface HTMLAttributes<T> {
      onclick_outside?: (e: CustomEvent) => void;
    }
  }
}
