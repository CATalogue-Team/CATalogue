import { render } from '@testing-library/svelte';
import { screen } from '@testing-library/dom';
import { describe, it, expect } from 'vitest';
import '@testing-library/jest-dom';
import CatProfile from '../src/lib/components/CatProfile.svelte';

interface CatProfileProps {
  cat: {
    id: string;
    name: string;
    age: number;
    breed?: string;
    photos: string[];
  };
  editable?: boolean;
}

describe('CatProfile Component', () => {
  const mockCat = {
    id: '1',
    name: '测试猫咪',
    age: 2,
    breed: '测试品种',
    photos: ['photo1.jpg', 'photo2.jpg']
  };

  it('渲染基础信息', () => {
    render(CatProfile, { 
      props: { cat: mockCat } as CatProfileProps
    });
    
    expect(screen.getByText(mockCat.name)).toBeInTheDocument();
    expect(screen.getByText(`年龄: ${mockCat.age}岁`)).toBeInTheDocument();
    expect(screen.getByText(`品种: ${mockCat.breed}`)).toBeInTheDocument();
  });

  it('不显示编辑按钮当editable为false', () => {
    render(CatProfile, { 
      props: { cat: mockCat, editable: false } as CatProfileProps
    });
    
    expect(screen.queryByText('编辑')).not.toBeInTheDocument();
    expect(screen.queryByText('删除')).not.toBeInTheDocument();
  });

  it('显示编辑按钮当editable为true', () => {
    render(CatProfile, {
      props: { cat: mockCat, editable: true } as CatProfileProps
    });
    
    expect(screen.getByText('编辑')).toBeInTheDocument();
    expect(screen.getByText('删除')).toBeInTheDocument();
  });
});
