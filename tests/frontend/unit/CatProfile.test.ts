import { render } from '@testing-library/svelte';
import { fireEvent } from '@testing-library/user-event';
import CatProfile from '../../../src/lib/components/CatProfile.svelte';

describe('CatProfile Component', () => {
  const mockCat = {
    id: '1',
    name: 'Fluffy',
    age: 3,
    breed: 'Persian',
    photos: ['photo1.jpg', 'photo2.jpg']
  };

  it('renders cat information correctly', () => {
    const { getByText } = render(CatProfile, {
      props: { cat: mockCat }
    });

    expect(getByText('Fluffy')).toBeInTheDocument();
    expect(getByText('年龄: 3岁')).toBeInTheDocument();
    expect(getByText('品种: Persian')).toBeInTheDocument();
  });

  it('emits edit event when edit button clicked', async () => {
    const { getByText, component } = render(CatProfile, {
      props: { cat: mockCat, editable: true }
    });

    const editHandler = vi.fn();
    component.$on('edit', editHandler);

    await fireEvent.click(getByText('编辑'));
    expect(editHandler).toHaveBeenCalledWith(expect.objectContaining({
      detail: { id: '1' }
    }));
  });

  it('does not show edit buttons when not editable', () => {
    const { queryByText } = render(CatProfile, {
      props: { cat: mockCat, editable: false }
    });

    expect(queryByText('编辑')).not.toBeInTheDocument();
  });
});
