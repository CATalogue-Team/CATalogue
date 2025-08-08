declare module './catStore.mock' {
  import { Readable } from 'svelte/store';
  import type { Cat } from '$lib/stores/cat.store';

  export const mockCatStore: {
    subscribe: Readable<{
      cats: Map<string, Cat>;
      loading: boolean;
      error: string | null;
    }>['subscribe'];
    setLoading: (loading: boolean) => void;
    setError: (error: string) => void;
    setCats: (cats: Cat[]) => void;
    reset: () => void;
  };
}

declare module '$lib/stores/cat.store' {
  import { Readable } from 'svelte/store';

  export interface Cat {
    id: string;
    name: string;
    age: number;
    photos: string[];
  }

  export const catStore: Readable<{
    cats: Map<string, Cat>;
    loading: boolean;
    error: string | null;
  }>;

  export function fetchCats(): Promise<void>;
}
