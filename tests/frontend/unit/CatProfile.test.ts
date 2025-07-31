import { render } from '@testing-library/svelte';
import { fireEvent } from '@testing-library/dom';
import { describe, it, expect, vi } from 'vitest';
import CatProfile from '$lib/components/CatProfile.svelte';

describe('CatProfile Component', () => {
  const mockCat = {
    id: '1',
    name: '测试猫咪',
    age: 2,
    breed: '测试品种',
    photos: ['photo1.jpg', 'photo2.jpg']
  };

  it('渲染基础信息', async () => {
    const { getByText } = render(CatProfile, { 
      props: { cat: mockCat },
      target: document.body
    });
    
    expect(getByText(mockCat.name)).toBeInTheDocument();
    expect(getByText(`年龄: ${mockCat.age}岁`)).toBeInTheDocument();
    expect(getByText(`品种: ${mockCat.breed}`)).toBeInTheDocument();
  });

  it('不显示编辑按钮当editable为false', async () => {
    const { queryByText } = render(CatProfile, { 
      props: { cat: mockCat, editable: false },
      target: document.body
    });
    
    expect(queryByText('编辑')).not.toBeInTheDocument();
    expect(queryByText('删除')).not.toBeInTheDocument();
  });

  it('显示编辑按钮当editable为true', async () => {
    const { getByText } = render(CatProfile, {
      props: { cat: mockCat, editable: true },
      target: document.body
    });
    
    expect(getByText('编辑')).toBeInTheDocument();
    expect(getByText('删除')).toBeInTheDocument();
  });

  it('不显示品种信息当breed未定义', async () => {
    const catWithoutBreed = {...mockCat, breed: undefined};
    const { queryByText } = render(CatProfile, {
      props: { cat: catWithoutBreed },
      target: document.body
    });
    
    expect(queryByText('品种:')).not.toBeInTheDocument();
  });

  it('触发编辑事件', async () => {
    const { getByText, component } = render(CatProfile, {
      props: { cat: mockCat, editable: true },
      target: document.body
    });
    
    const mockHandler = vi.fn();
    component.$on('edit', mockHandler);
    
    fireEvent.click(getByText('编辑'));
    expect(mockHandler).toHaveBeenCalled();
  });

  it('触发删除事件', async () => {
    const { getByText, component } = render(CatProfile, {
      props: { cat: mockCat, editable: true },
      target: document.body
    });
    
    const mockHandler = vi.fn();
    component.$on('delete', mockHandler);
    
    fireEvent.click(getByText('删除'));
    expect(mockHandler).toHaveBeenCalled();
  });
});
