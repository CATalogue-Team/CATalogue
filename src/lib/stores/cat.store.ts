import { writable } from 'svelte/store';

interface Cat {
  id: string;
  name: string;
  age: number;
  breed?: string;
  photos: string[];
}

interface CatState {
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
    // TODO: Replace with actual API call
    const mockCats: Cat[] = [
      {
        id: '1',
        name: '小花',
        age: 2,
        breed: '英国短毛猫',
        photos: []
      },
      {
        id: '2',
        name: '小黑',
        age: 3,
        photos: []
      }
    ];

    const catsMap = new Map(mockCats.map(cat => [cat.id, cat]));
    
    catStore.update(state => ({
      ...state,
      cats: catsMap,
      loading: false
    }));
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err.message,
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
      error: err.message,
      loading: false
    }));
  }
};
