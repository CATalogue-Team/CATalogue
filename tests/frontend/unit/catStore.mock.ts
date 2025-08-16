import { writable } from 'svelte/store';
import type { Cat } from '$lib/stores/cat.store';

type CatStoreState = {
  cats: Map<string, Cat>;
  loading: boolean;
  error: string | null;
};

const createMockStore = () => {
  const store = writable<CatStoreState>({
    cats: new Map(),
    loading: true,
    error: null
  });

  return {
    subscribe: store.subscribe,
    setLoading: (loading: boolean) => store.update(s => ({...s, loading})),
    setError: (error: string) => store.update(s => ({...s, error})),
    setCats: (cats: Cat[]) => store.update(s => ({
      ...s,
      cats: new Map(cats.map(cat => [cat.id, cat]))
    })),
    reset: () => store.set({
      cats: new Map(),
      loading: true,
      error: null
    })
  };
};

export const mockFetchCats = vi.fn().mockImplementation(async () => {
  mockCatStore.setLoading(true);
  await new Promise(resolve => setTimeout(resolve, 50));
  mockCatStore.setCats([{
    id: '1',
    name: '猫咪1',
    birth_date: '2023-08-16',
    photos: [],
    breed: '田园猫',
    owner_id: 'user1',
    created_at: '2023-08-16T00:00:00Z',
    updated_at: '2023-08-16T00:00:00Z'
  }]);
  mockCatStore.setLoading(false);
  return true;
});

// 添加全局mock
vi.mock('$lib/stores/cat.store', () => ({
  catStore: mockCatStore,
  fetchCats: mockFetchCats
}));

// 添加全局mock
vi.mock('$lib/stores/cat.store', () => ({
  catStore: mockCatStore,
  fetchCats: mockFetchCats
}));

export const mockCatStore = {
  ...createMockStore(),
  fetchCats: mockFetchCats,
  $subscribe: vi.fn()
};
