import { writable } from 'svelte/store';

export interface Cat {
  id: string;
  name: string;
  age: number;
  breed?: string;
  photos: string[];
  editable?: boolean;
  growthRecords?: {
    id: string,
    date: string,
    weight: number,
    height: number,
    notes: string,
    photos: string[]
  }[]
}

export interface CatState {
  cats: Map<string, Cat>;
  loading: boolean;
  error: string | null;
}

const initialState: CatState = {
  cats: new Map(),
  loading: false,
  error: null
};

export const catStore = writable<CatState>(initialState);

export const fetchCats = async () => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    const response = await fetch('/api/v1/cats');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const cats: Cat[] = await response.json();
    const catsMap = new Map(cats.map(cat => [cat.id, cat]));
    
    catStore.update(state => ({
      ...state,
      cats: catsMap,
      loading: false
    }));
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
  }
};

export const fetchCat = async (id: string) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    // TODO: Replace with actual API call
    const mockCat: Cat = {
      id,
      name: '模拟猫咪',
      age: 1,
      photos: []
    };

    catStore.update(state => {
      const newCats = new Map(state.cats);
      newCats.set(id, mockCat);
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
  }
};
