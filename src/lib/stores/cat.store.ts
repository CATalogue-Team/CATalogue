import { writable } from 'svelte/store';
import type { GrowthRecord } from '../types.js';

function calculateAge(birthDate: string): number {
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

export interface Cat {
  id: string;
  name: string;
  birth_date?: string;
  breed?: string;
  photos: string[];
  editable?: boolean;
  owner_id: string;
  created_at?: string;
  updated_at?: string;
  age?: number;
  growthRecords?: GrowthRecord[];
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
    const data = await response.json();
    const cats: Cat[] = data.map(cat => ({
      ...cat,
      age: cat.birth_date ? calculateAge(cat.birth_date) : 0
    }));
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
    const data = await response.json();
    const cat: Cat = {
      ...data,
      age: data.birth_date ? calculateAge(data.birth_date) : 0
    };
    
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

export const createCat = async (catData: Omit<Cat, 'id' | 'age'>) => {
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

    const data = await response.json();
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

export const updateCat = async (id: string, catData: Partial<Omit<Cat, 'id' | 'age'>>) => {
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

    const data = await response.json();
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

    const data = await response.json();
    
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

// TODO: 等待后端API实现
// 成长记录相关方法(当前为模拟实现)
export const createGrowthRecord = async (catId: string, record: Omit<GrowthRecord, 'id'>) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    // 模拟API调用
    const newRecord: GrowthRecord = {
      id: `gr-${Date.now()}`,
      ...record,
      photos: []
    };

    // 更新store中的猫咪成长记录
    catStore.update(state => {
      const newCats = new Map(state.cats);
      const cat = newCats.get(catId);
      if (cat) {
        newCats.set(catId, {
          ...cat,
          growthRecords: [...(cat.growthRecords || []), newRecord]
        });
      }
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
    return newRecord;
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
    throw err;
  }
};

export const updateGrowthRecord = async (catId: string, recordId: string, record: Partial<GrowthRecord>) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    // 模拟API调用
    catStore.update(state => {
      const newCats = new Map(state.cats);
      const cat = newCats.get(catId);
      if (cat && cat.growthRecords) {
        const updatedRecords = cat.growthRecords.map(r => 
          r.id === recordId ? { ...r, ...record } : r
        );
        newCats.set(catId, {
          ...cat,
          growthRecords: updatedRecords
        });
      }
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
    return true;
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
    throw err;
  }
};

export const deleteGrowthRecord = async (catId: string, recordId: string) => {
  catStore.update(state => ({
    ...state,
    loading: true,
    error: null
  }));

  try {
    // 模拟API调用
    catStore.update(state => {
      const newCats = new Map(state.cats);
      const cat = newCats.get(catId);
      if (cat && cat.growthRecords) {
        const updatedRecords = cat.growthRecords.filter(r => r.id !== recordId);
        newCats.set(catId, {
          ...cat,
          growthRecords: updatedRecords
        });
      }
      return {
        ...state,
        cats: newCats,
        loading: false
      };
    });
    return true;
  } catch (err) {
    catStore.update(state => ({
      ...state,
      error: err instanceof Error ? err.message : 'Unknown error',
      loading: false
    }));
    throw err;
  }
};
