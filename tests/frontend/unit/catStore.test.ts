import { vi, describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { 
  catStore, 
  fetchCats, 
  fetchCat,
  createCat,
  updateCat,
  deleteCat,
  uploadCatPhotos
} from '../../../src/lib/stores/cat.store.ts';
import type { Cat } from '../../../src/lib/stores/cat.store.ts';

describe('catStore', () => {
  const mockCat1: Cat = {
    id: '1',
    name: '小花',
    age: 2,
    breed: '英国短毛猫',
    photos: []
  };
  
  beforeEach(() => {
    // 重置store状态
    catStore.set({
      cats: new Map(),
      loading: false,
      error: null
    });
    vi.restoreAllMocks();
  });

  describe('fetchCats', () => {
    it('should update store with cats on success', async () => {
      // Mock API response
      const mockResponse = [
        {
          id: '1',
          name: '小花',
          age: 2,
          breed: '英国短毛猫',
          photos: [],
        },
        {
          id: '2',
          name: '小黑',
          age: 3,
          photos: []
        }
      ];
      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      } as Response);

      await fetchCats();
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.size).toBe(2);
      expect(state.cats.get('1')?.name).toBe('小花');
      expect(state.cats.get('2')?.name).toBe('小黑');
    });

    it('should handle error', async () => {
      const mockError = new Error('API error');
      vi.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      try {
        await fetchCats();
      } catch (err) {
        const state = get(catStore);
        expect(state.loading).toBe(false);
        expect(state.error).toBe('API error');
        expect(state.cats.size).toBe(0);
      }
    });

    it('should set loading state during fetch', async () => {
      let resolveFetch: (value?: unknown) => void;
      const promise = new Promise(resolve => {
        resolveFetch = resolve;
      });
      vi.spyOn(global, 'fetch').mockReturnValueOnce(promise as Promise<Response>);

      const fetchPromise = fetchCats();
      
      const loadingState = get(catStore);
      expect(loadingState.loading).toBe(true);

      resolveFetch!();
      await fetchPromise;
    });
  });

  describe('fetchCat', () => {
    it('should add cat to store on success', async () => {
      const mockCat = {
        id: '3',
        name: '测试猫咪',
        age: 1,
        photos: []
      };
      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCat)
      } as Response);

      await fetchCat('3');
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.size).toBe(1);
      expect(state.cats.get('3')?.name).toBe('测试猫咪');
    });

    it('should handle error', async () => {
      const mockError = new Error('API error');
      vi.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      try {
        await fetchCat('1');
      } catch (err) {
        const state = get(catStore);
        expect(state.loading).toBe(false);
        expect(state.error).toBe('API error');
        expect(state.cats.size).toBe(0);
      }
    });

    it('should update existing cat', async () => {
      catStore.update(state => ({
        ...state,
        cats: new Map([['1', mockCat1]])
      }));

      const updatedCat = {
        ...mockCat1,
        name: '更新后的名字'
      };
      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedCat)
      } as Response);

      await fetchCat('1');
      
      const state = get(catStore);
      expect(state.cats.get('1')?.name).toBe('更新后的名字');
    });
  });

  describe('createCat', () => {
    it('should add new cat to store on success', async () => {
      const newCat = {
        id: '3',
        name: '新猫咪',
        age: 1,
        photos: []
      };
      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(newCat)
      } as Response);

      const result = await createCat({
        name: '新猫咪',
        age: 1,
        photos: []
      });
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.size).toBe(1);
      expect(state.cats.get('3')?.name).toBe('新猫咪');
      expect(result).toEqual(newCat);
    });

    it('should handle error', async () => {
      const mockError = new Error('API error');
      vi.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      try {
        await createCat({
          name: '新猫咪',
          age: 1,
          photos: []
        });
      } catch (err) {
        const state = get(catStore);
        expect(state.loading).toBe(false);
        expect(state.error).toBe('API error');
        expect(state.cats.size).toBe(0);
      }
    });
  });

  describe('updateCat', () => {
    it('should update existing cat in store', async () => {
      catStore.update(state => ({
        ...state,
        cats: new Map([['1', mockCat1]])
      }));

      const updatedCat = {
        ...mockCat1,
        name: '更新后的名字'
      };
      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedCat)
      } as Response);

      const result = await updateCat('1', { name: '更新后的名字' });
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.size).toBe(1);
      expect(state.cats.get('1')?.name).toBe('更新后的名字');
      expect(result).toEqual(updatedCat);
    });

    it('should handle error', async () => {
      const mockError = new Error('API error');
      vi.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      try {
        await updateCat('1', { name: '新名字' });
      } catch (err) {
        const state = get(catStore);
        expect(state.loading).toBe(false);
        expect(state.error).toBe('API error');
      }
    });
  });

  describe('deleteCat', () => {
    it('should remove cat from store on success', async () => {
      catStore.update(state => ({
        ...state,
        cats: new Map([['1', mockCat1]])
      }));

      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      } as Response);

      await deleteCat('1');
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.size).toBe(0);
    });

    it('should handle error', async () => {
      const mockError = new Error('API error');
      vi.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      try {
        await deleteCat('1');
      } catch (err) {
        const state = get(catStore);
        expect(state.loading).toBe(false);
        expect(state.error).toBe('API error');
      }
    });
  });

  describe('uploadCatPhotos', () => {
    it('should add photos to cat in store', async () => {
      catStore.update(state => ({
        ...state,
        cats: new Map([['1', mockCat1]])
      }));

      const mockResponse = {
        photos: ['photo1.jpg', 'photo2.jpg']
      };
      vi.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      } as Response);

      const result = await uploadCatPhotos('1', [new File([], 'test.jpg')]);
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.get('1')?.photos).toEqual(['photo1.jpg', 'photo2.jpg']);
      expect(result).toEqual(mockResponse);
    });

    it('should handle error', async () => {
      const mockError = new Error('API error');
      vi.spyOn(global, 'fetch').mockRejectedValueOnce(mockError);

      try {
        await uploadCatPhotos('1', [new File([], 'test.jpg')]);
      } catch (err) {
        const state = get(catStore);
        expect(state.loading).toBe(false);
        expect(state.error).toBe('API error');
      }
    });
  });

  describe('store state', () => {
    it('should have initial state', () => {
      const state = get(catStore);
      expect(state).toEqual({
        cats: new Map(),
        loading: false,
        error: null
      });
    });

    it('should update cats map correctly', () => {
      catStore.update(state => ({
        ...state,
        cats: new Map([['1', mockCat1]])
      }));

      const state = get(catStore);
      expect(state.cats.size).toBe(1);
      expect(state.cats.get('1')).toEqual(mockCat1);
    });
  });
});
