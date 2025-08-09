import { writable } from 'svelte/store';
import type { GrowthRecord } from '../types.js';

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
    const { data } = await response.json();
    const cats: Cat[] = data;
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
    const response = await fetch(`/api/v1/cats/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const { data } = await response.json();
    const cat: Cat = data;
    
    catStore.update(state => {
      const newCats = new Map(state.cats);
      newCats.set(id, cat);
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

export const createCat = async (catData: Omit<Cat, 'id'>) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    const response = await fetch('/api/v1/cats', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(catData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const { data } = await response.json();
    const newCat: Cat = data;
    
    catStore.update(state => {
      const newCats = new Map(state.cats);
      newCats.set(newCat.id, newCat);
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
    return newCat;
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
    throw err;
  }
};

export const updateCat = async (id: string, catData: Partial<Cat>) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    const response = await fetch(`/api/v1/cats/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(catData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const { data } = await response.json();
    const updatedCat: Cat = data;
    
    catStore.update(state => {
      const newCats = new Map(state.cats);
      newCats.set(id, updatedCat);
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
    return updatedCat;
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
    throw err;
  }
};

export const deleteCat = async (id: string) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    const response = await fetch(`/api/v1/cats/${id}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    catStore.update(state => {
      const newCats = new Map(state.cats);
      newCats.delete(id);
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
    throw err;
  }
};

export const uploadCatPhotos = async (catId: string, files: File[]) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`/api/v1/cats/${catId}/photos`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const { data } = await response.json();
    
    // 更新store中的猫咪照片
    catStore.update(state => {
      const newCats = new Map(state.cats);
      const cat = newCats.get(catId);
      if (cat) {
        newCats.set(catId, {
          ...cat,
          photos: [...cat.photos, ...data.photos]
        });
      }
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
    return data;
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
    throw err;
  }
};
