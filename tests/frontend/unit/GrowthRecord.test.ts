import { render } from '@testing-library/svelte';
import { fireEvent } from '@testing-library/dom';
import GrowthRecordComponent from '../../../src/lib/components/GrowthRecord/GrowthRecord.svelte';
import type { GrowthRecord } from '../../../src/lib/types.js';

describe('GrowthRecord Component', () => {
  const mockRecord: GrowthRecord = {
    id: '1',
    date: '2025-01-01',
    weight: 4.5,
    height: 25,
    notes: 'Healthy growth',
    photos: ['photo1.jpg', 'photo2.jpg']
  };

  it('renders record information correctly', () => {
    const { getByText } = render(GrowthRecordComponent, {
      props: { record: mockRecord }
    });

    expect(getByText('2025-01-01')).toBeInTheDocument();
    expect(getByText(/体重:.*4.5kg/)).toBeInTheDocument();
    expect(getByText(/身高:.*25cm/)).toBeInTheDocument();
    expect(getByText(/备注:.*Healthy growth/)).toBeInTheDocument();
  });

  it('renders without optional fields', () => {
    const minimalRecord: GrowthRecord = {
      id: '1',
      date: new Date().toISOString().split('T')[0],
      photos: []
    };
    
    const { queryByText } = render(GrowthRecordComponent, {
      props: { record: minimalRecord }
    });

    expect(queryByText('体重:')).not.toBeInTheDocument();
    expect(queryByText('身高:')).not.toBeInTheDocument();
    expect(queryByText('备注:')).not.toBeInTheDocument();
  });

  it('dispatches add event when adding new record', async () => {
    const { component, getByText } = render(GrowthRecordComponent, {
      props: { record: null, editable: true }
    });

    const mockHandler = vi.fn();
    component.$on('add', mockHandler);

    fireEvent.click(getByText('添加记录'));
    expect(mockHandler).toHaveBeenCalled();
  });

  it('dispatches delete event', async () => {
    const { component, getByText } = render(GrowthRecordComponent, {
      props: { record: mockRecord, editable: true }
    });

    const mockHandler = vi.fn();
    component.$on('delete', mockHandler);

    fireEvent.click(getByText('删除'));
    expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({
      detail: { id: '1' }
    }));
  });

  it('forwards photoUpload event from form', async () => {
    const { component, getByText, queryByText } = render(GrowthRecordComponent, {
      props: { record: mockRecord, editable: true }
    });

    const mockHandler = vi.fn();
    component.$on('photoUpload', mockHandler);

    // 点击编辑按钮进入编辑模式
    fireEvent.click(getByText('编辑'));
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // 通过DOM验证是否进入编辑模式
    expect(queryByText('保存')).toBeInTheDocument();
    
    // 模拟文件上传
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
      fireEvent.change(fileInput, {
        target: {
          files: [new File([''], 'test.jpg', { type: 'image/jpeg' })]
        }
      });
    }
    
    expect(mockHandler).toHaveBeenCalled();
  });

  it('forwards edit event from form', async () => {
    const { component, getByText, queryByText } = render(GrowthRecordComponent, {
      props: { record: mockRecord, editable: true }
    });

    const mockHandler = vi.fn();
    component.$on('edit', mockHandler);

    // 点击编辑按钮进入编辑模式
    fireEvent.click(getByText('编辑'));
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // 通过DOM验证是否进入编辑模式
    expect(queryByText('保存')).toBeInTheDocument();
    
    // 点击保存按钮触发编辑事件
    fireEvent.click(getByText('保存'));
    
    expect(mockHandler).toHaveBeenCalled();
  });

  it('toggles edit mode when edit button clicked', async () => {
    const { getByText, queryByText } = render(GrowthRecordComponent, {
      props: { record: mockRecord, editable: true }
    });

    // 初始状态应为显示模式
    expect(queryByText('编辑')).toBeInTheDocument();
    expect(queryByText('保存')).not.toBeInTheDocument();

    // 点击编辑按钮进入编辑模式
    fireEvent.click(getByText('编辑'));
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // 验证是否显示保存按钮
    expect(queryByText('保存')).toBeInTheDocument();
    expect(queryByText('编辑')).not.toBeInTheDocument();

    // 点击取消按钮返回显示模式
    fireEvent.click(getByText('取消'));
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // 验证是否恢复显示编辑按钮
    expect(queryByText('编辑')).toBeInTheDocument();
    expect(queryByText('保存')).not.toBeInTheDocument();
  });

  it('hides edit buttons when not editable', () => {
    const { queryByText } = render(GrowthRecordComponent, {
      props: { record: mockRecord, editable: false }
    });

    expect(queryByText('编辑')).not.toBeInTheDocument();
    expect(queryByText('删除')).not.toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(GrowthRecordComponent, {
      props: { record: mockRecord }
    });

    expect(container.querySelector('.growth-record')).toBeInTheDocument();
    expect(container.querySelector('.record-display')).toBeInTheDocument();
  });

  it('shows add button when no record and editable', () => {
    const { getByText } = render(GrowthRecordComponent, {
      props: { record: null, editable: true }
    });

    expect(getByText('添加记录')).toBeInTheDocument();
  });
});
