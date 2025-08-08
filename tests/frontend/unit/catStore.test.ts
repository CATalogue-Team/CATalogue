import { vi, describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { catStore, fetchCats, fetchCat } from '../../../src/lib/stores/cat.store.ts';
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
      // 模拟错误
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
      
      // 检查加载状态
      const loadingState = get(catStore);
      expect(loadingState.loading).toBe(true);

      resolveFetch!();
      await fetchPromise;
    });
  });

  describe('fetchCat', () => {
    it('should add cat to store on success', async () => {
      const catId = '3';
      await fetchCat(catId);
      
      const state = get(catStore);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.cats.size).toBe(1);
      expect(state.cats.get(catId)?.name).toBe('模拟猫咪');
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
      // 先添加一个猫咪
      catStore.update(state => ({
        ...state,
        cats: new Map([['1', mockCat1]])
      }));

      // 更新猫咪
      await fetchCat('1');
      
      const state = get(catStore);
      expect(state.cats.get('1')?.name).toBe('模拟猫咪');
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
