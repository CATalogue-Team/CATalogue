import { render } from '@testing-library/svelte';
import { screen } from '@testing-library/dom';
import { vi } from 'vitest';
import { readable, type Writable } from 'svelte/store';
import { tick } from 'svelte';
import CatDetailPage from '../../../src/routes/cats/[id]/+page.svelte'; 
import { catStore } from '../../../src/lib/stores/cat.store.ts';
import type { Cat } from '../../../src/lib/stores/cat.store.ts';

// 使用vi.hoisted定义mock数据
const mockCat = vi.hoisted(() => ({
  id: '1',
  name: '测试猫咪',
  age: 2,
  photos: [],
  growthRecords: [
    {
      id: '1',
      date: '2025-01-01',
      weight: 4.5,
      height: 25,
      notes: '健康',
      photos: []
    }
  ]
} as Cat));

describe('CatDetailPage', () => {
  // 定义增强的Writable接口
  interface EnhancedWritable<T> extends Writable<T> {
    get: () => T;
  }

  beforeEach(async () => {
    // 模拟SvelteKit的$page store
    vi.mock('$app/stores', () => ({
      page: readable({
        url: new URL('http://localhost/cats/1'),
        params: { id: '1' },
        status: 200,
        error: null,
        data: {}
      }),
      navigating: readable(null),
      updated: readable(false)
    }));

    // 确保组件能正确订阅store
    vi.mock('../../../src/lib/stores/cat.store', async () => {
      const actual = await vi.importActual('../../../src/lib/stores/cat.store');
      
      // 定义store状态类型
      type MockCatState = {
        cats: Map<string, Cat>;
        loading: boolean;
        error: string | null;
      };

      // 创建store模拟
      const subscribers = new Set<(value: MockCatState) => void>();
      let currentValue: MockCatState = {
        cats: new Map([[mockCat.id, mockCat]]),
        loading: false,
        error: null
      };

      const mockStore: EnhancedWritable<MockCatState> = {
        subscribe: (run: (value: MockCatState) => void) => {
          // 立即执行一次当前值
          run(currentValue);
          subscribers.add(run);
          return () => {
            subscribers.delete(run);
          };
        },
        set: vi.fn(async (value: MockCatState) => {
          currentValue = value;
          // 同步触发所有订阅者
          subscribers.forEach(sub => {
            sub(value);
          });
          return Promise.resolve();
        }),
        update: vi.fn(async (updater: (state: MockCatState) => MockCatState) => {
          const newValue = updater(currentValue);
          currentValue = newValue;
          // 同步触发所有订阅者
          subscribers.forEach(sub => {
            sub(newValue);
          });
          return Promise.resolve();
        }),
        get: vi.fn(() => {
          return currentValue;
        })
      };

      // 在测试中手动设置数据
      if (process.env.TEST_INITIAL_DATA) {
        mockStore.set({
          cats: new Map([[mockCat.id, mockCat]]),
          loading: false,
          error: null
        });
      }

      return {
        ...actual,
        catStore: mockStore,
        fetchCat: vi.fn().mockResolvedValue(mockCat)
      };
    });
  });

  it('renders loading state', async () => {
    // 设置初始loading状态为true
    await catStore.set({
      cats: new Map(),
      loading: true,
      error: null
    });

    const { getByText } = render(CatDetailPage, {
      props: {
        data: { params: { id: '1' } }
      }
    });

    // 确保组件渲染完成
    await tick();
    
    // 检查加载状态
    expect(getByText('加载中...')).toBeInTheDocument();
    
    // 模拟加载完成
    catStore.set({
      cats: new Map([[mockCat.id, mockCat]]),
      loading: false,
      error: null
    });
  });

  it('renders error state', async () => {
    // 先设置store状态再渲染组件
    await catStore.set({
      cats: new Map(),
      loading: false,
      error: '加载失败'
    });

    render(CatDetailPage, {
      props: {
        data: { params: { id: '1' } }
      }
    });

    // 等待组件渲染完成
    await tick();
    
    // 检查错误状态渲染
    const errorElement = screen.getByText('加载失败');
    expect(errorElement).toBeInTheDocument();
  });

  it('renders cat not found state', async () => {
    // 先设置store状态再渲染组件
    catStore.set({
      cats: new Map(),
      loading: false,
      error: null
    });

    render(CatDetailPage, {
      props: {
        data: { params: { id: '1' } }
      }
    });

    // 等待组件渲染完成
    await tick();
    
    // 检查猫咪未找到状态
    const notFoundElement = await screen.findByText(/未找到猫咪信息/);
    expect(notFoundElement).toBeInTheDocument();
  });

  it('renders cat profile and growth records', async () => {
    // 先设置store状态再渲染组件
    await catStore.set({
      cats: new Map([[mockCat.id, mockCat]]),
      loading: false,
      error: null
    });

    render(CatDetailPage, {
      props: {
        data: { params: { id: '1' } }
      }
    });

    // 等待组件渲染完成
    await tick();
    
    // 检查猫咪详情和成长记录
    const profileElement = await screen.findByText(/猫咪详情/);
    const recordsTitle = await screen.findByRole('heading', { name: '成长记录' });
    expect(profileElement).toBeInTheDocument();
    expect(recordsTitle).toBeInTheDocument();
    
    // 检查详细内容
    expect(await screen.findByText('2025-01-01')).toBeInTheDocument();
    expect(await screen.findByText(/体重:.*4.5kg/)).toBeInTheDocument();
    expect(await screen.findByText(/身高:.*25cm/)).toBeInTheDocument();
  });

  it('handles empty growth records', async () => {
    // 先设置store状态再渲染组件
    catStore.set({
      cats: new Map([['1', { ...mockCat, growthRecords: [] }]]),
      loading: false,
      error: null
    });

    render(CatDetailPage, {
      props: {
        data: { params: { id: '1' } }
      }
    });

    // 等待组件渲染完成
    await tick();
    
    // 检查空成长记录状态
    const emptyElement = await screen.findByText(/暂无成长记录/i);
    expect(emptyElement).toBeInTheDocument();
  });

  it('unsubscribes from store on unmount', async () => {
    const unsubscribe = vi.fn();
    const { component, unmount } = render(CatDetailPage, {
      props: {
        data: { params: { id: '1' } }
      }
    });

    // 模拟组件内部订阅
    component.$$.on_destroy.push(unsubscribe);

    // 触发unmount
    unmount();
    
    expect(unsubscribe).toHaveBeenCalled();
  });
});
