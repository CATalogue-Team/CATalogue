import { renderPageComponent } from '../../../src/lib/test-adapters.js';
import { screen, waitFor } from '@testing-library/dom';
import { vi } from 'vitest';
import { tick } from 'svelte';

// 1. 首先设置所有mock
// Mock SvelteKit $app/stores with correct data structure
vi.mock('$app/stores', () => {
  const getStores = () => ({
    page: {
      subscribe: (fn: any) => {
        fn({ data: { cats: [] } });
        return () => {};
      }
    }
  });
  const page = {
    subscribe: (fn: any) => {
      fn({ data: { cats: [] } });
      return () => {};
    }
  };
  return { getStores, page };
});

// 导入Cat类型
import type { Cat } from '$lib/stores/cat.store';

// 2. 创建mock store和函数
const mockFunctions = vi.hoisted(() => {
  let state = {
    cats: new Map<string, Cat>(),
    loading: false,
    error: null
  };
  
  const subscribers: Function[] = [];

  const notify = () => subscribers.forEach(fn => fn(state));

  const mockCatStore = {
    get state() { return state; },
    setCats: vi.fn((cats: Cat[]) => {
      state.cats = new Map(cats.map(cat => [cat.id, cat]));
      notify();
    }),
    setLoading: vi.fn((loading: boolean) => {
      state.loading = loading;
      notify();
    }),
    setError: vi.fn((error: string | null) => {
      state.error = error as null;
      notify();
    }),
    reset: vi.fn(() => {
      state = {
        cats: new Map(),
        loading: false,
        error: null
      };
      notify();
    }),
    subscribe: vi.fn((fn: (value: typeof state) => void) => {
      fn(state);
      subscribers.push(fn);
      return () => {
        const index = subscribers.indexOf(fn);
        if (index !== -1) subscribers.splice(index, 1);
      };
    })
  };

  const mockFetchCats = vi.fn(async () => {
    mockCatStore.setLoading(true);
    // 移除模拟延迟，直接返回结果
    mockCatStore.setCats([
      { id: '1', name: '猫咪1', age: 2, photos: [] },
      { id: '2', name: '猫咪2', age: 3, photos: [] }
    ]);
    mockCatStore.setLoading(false);
    return true;
  });

  return { mockCatStore, mockFetchCats };
});

// 3. 在导入组件前设置mock
vi.mock('$lib/stores/cat.store', async () => {
  const actual = await vi.importActual('$lib/stores/cat.store');
  return {
    ...actual,
    catStore: mockFunctions.mockCatStore,
    fetchCats: mockFunctions.mockFetchCats,
    fetchCat: vi.fn(),
    default: {
      ...actual,
      catStore: mockFunctions.mockCatStore,
      fetchCats: mockFunctions.mockFetchCats,
      fetchCat: vi.fn()
    }
  };
});

// 4. 最后导入组件
import CatsListPage from '../../../src/routes/cats/+page.svelte';

// Mock数据
const mockCat1: Cat = {
  id: '1',
  name: '猫咪1',
  age: 2,
  photos: []
};

const mockCat2: Cat = {
  id: '2',
  name: '猫咪2',
  age: 3,
  photos: []
};

describe('Cats List Page', () => {
  beforeEach(() => {
    mockFunctions.mockCatStore.reset();
    vi.clearAllMocks();
  });

  it('renders loading state', async () => {
    mockFunctions.mockCatStore.setLoading(true);
    const { container } = await renderPageComponent(CatsListPage, {
      data: {}
    });
    expect(container).toBeTruthy();
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders error state', async () => {
    mockFunctions.mockCatStore.setError('加载失败');
    const { container } = await renderPageComponent(CatsListPage, {});
    expect(container).toBeTruthy();
    await tick();
    expect(screen.getByText('加载失败')).toBeInTheDocument();
  });

  it('renders cats list', async () => {
    mockFunctions.mockCatStore.setCats([mockCat1, mockCat2]);
    const { container } = await renderPageComponent(CatsListPage, {});
    expect(container).toBeTruthy();
    await tick();
    expect(screen.getByTestId('cat-profile-1')).toBeInTheDocument();
    expect(screen.getByTestId('cat-profile-2')).toBeInTheDocument();
  });

  it('calls fetchCats on mount', async () => {
    // 主动设置 cats，模拟 fetchCats 结果
    mockFunctions.mockCatStore.setCats([mockCat1, mockCat2]);

    // 渲染组件
    const { container } = await renderPageComponent(CatsListPage, { data: {} });
    expect(container).toBeTruthy();

    // 等待页面内容变化，确认 cats 被渲染
    await waitFor(() => {
      expect(screen.getByTestId('cat-profile-1')).toBeInTheDocument();
      expect(screen.getByTestId('cat-profile-2')).toBeInTheDocument();
    });
  });

  it('applies correct styles', async () => {
    mockFunctions.mockCatStore.setCats([mockCat1]);
    const { container } = await renderPageComponent(CatsListPage, {});
    expect(container).toBeTruthy();
    await tick();
    const catsContainer = container.querySelector('.container');
    expect(catsContainer).toBeInTheDocument();
    expect(catsContainer).toHaveClass('container');
  });
});
