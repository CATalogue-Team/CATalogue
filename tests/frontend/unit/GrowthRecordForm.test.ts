import { render } from '@testing-library/svelte';
import { fireEvent } from '@testing-library/dom';
import GrowthRecordForm from '../../../src/lib/components/GrowthRecord/GrowthRecordForm.svelte';
import type { GrowthRecord } from '../../../src/lib/types.js';

describe('GrowthRecordForm Component', () => {
  const mockRecord: GrowthRecord = {
    id: '1',
    date: '2025-01-01',
    weight: 4.5,
    height: 25,
    notes: 'Healthy growth',
    photos: ['photo1.jpg', 'photo2.jpg']
  };

  it('initializes form with record data', () => {
    const { getByDisplayValue } = render(GrowthRecordForm, {
      props: { record: mockRecord }
    });

    expect(getByDisplayValue('2025-01-01')).toBeInTheDocument();
    expect(getByDisplayValue('4.5')).toBeInTheDocument();
    expect(getByDisplayValue('25')).toBeInTheDocument();
    expect(getByDisplayValue('Healthy growth')).toBeInTheDocument();
  });

  it('dispatches save event with form data', async () => {
    const { component, getByText } = render(GrowthRecordForm, {
      props: { record: mockRecord }
    });

    const mockHandler = vi.fn();
    component.$on('save', mockHandler);

    fireEvent.click(getByText('保存'));
    expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({
      detail: {
        id: '1',
        record: expect.objectContaining({
          date: '2025-01-01',
          weight: 4.5,
          height: 25,
          notes: 'Healthy growth'
        })
      }
    }));
  });

  it('dispatches cancel event', async () => {
    const { component, getByText } = render(GrowthRecordForm);

    const mockHandler = vi.fn();
    component.$on('cancel', mockHandler);

    fireEvent.click(getByText('取消'));
    expect(mockHandler).toHaveBeenCalled();
  });

  it('validates required fields', async () => {
    const { component, getByLabelText, container } = render(GrowthRecordForm, {
      props: { record: { ...mockRecord, date: '' } }
    });

    const mockHandler = vi.fn();
    component.$on('error', mockHandler);

    const form = container.querySelector('form');
    if (!form) {
      throw new Error('Form not found');
    }

    fireEvent.submit(form);
    
    expect(mockHandler).toHaveBeenCalled();
    const errorMessage = mockHandler.mock.calls[0][0].detail;
    expect(errorMessage).toContain('日期不能为空');
  });

  it('validates weight field (<=0)', async () => {
    const { component, container } = render(GrowthRecordForm, {
      props: { record: { ...mockRecord, weight: 0 } }
    });

    const mockHandler = vi.fn();
    component.$on('error', mockHandler);

    const form = container.querySelector('form');
    if (!form) {
      throw new Error('Form not found');
    }

    fireEvent.submit(form);
    
    expect(mockHandler).toHaveBeenCalled();
    const errorMessage = mockHandler.mock.calls[0][0].detail;
    expect(errorMessage).toContain('体重必须大于0');
  });

  it('validates height field (<=0)', async () => {
    const { component, container } = render(GrowthRecordForm, {
      props: { record: { ...mockRecord, height: -0.1 } }
    });

    const mockHandler = vi.fn();
    component.$on('error', mockHandler);

    const form = container.querySelector('form');
    if (!form) {
      throw new Error('Form not found');
    }

    fireEvent.submit(form);
    
    expect(mockHandler).toHaveBeenCalled();
    const errorMessage = mockHandler.mock.calls[0][0].detail;
    expect(errorMessage).toContain('身高必须大于0');
  });

  it('dispatches photoUpload event', async () => {
    const { component, container } = render(GrowthRecordForm);

    const mockHandler = vi.fn();
    component.$on('photoUpload', mockHandler);

    // 模拟文件上传
    const fileInput = container.querySelector('input[type="file"]');
    if (!fileInput) {
      throw new Error('File input not found');
    }
    
    fireEvent.change(fileInput, {
      target: {
        files: [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      }
    });
    
    expect(mockHandler).toHaveBeenCalled();
  });

  it('shows error message', () => {
    const { getByText } = render(GrowthRecordForm, {
      props: { saveError: '保存失败' }
    });

    expect(getByText('保存失败')).toBeInTheDocument();
  });

  it('initializes empty form when no record provided', () => {
    const { queryByDisplayValue, container } = render(GrowthRecordForm);

    expect(queryByDisplayValue('2025-01-01')).not.toBeInTheDocument();
    expect(queryByDisplayValue('4.5')).not.toBeInTheDocument();
    expect(queryByDisplayValue('25')).not.toBeInTheDocument();
    expect(queryByDisplayValue('Healthy growth')).not.toBeInTheDocument();

    // 测试FileUpload组件存在
    const fileUpload = container.querySelector('[data-testid="file-upload"]');
    expect(fileUpload).toBeInTheDocument();
  });

  it('handles empty photos array', async () => {
    const { component, container } = render(GrowthRecordForm, {
      props: {
        record: {
          ...mockRecord,
          photos: []
        }
      }
    });

    const mockHandler = vi.fn();
    component.$on('save', mockHandler);

    const form = container.querySelector('form');
    if (!form) {
      throw new Error('Form not found');
    }

    fireEvent.submit(form);
    
    expect(mockHandler).toHaveBeenCalled();
    const savedData = mockHandler.mock.calls[0][0].detail.record;
    expect(savedData.photos).toEqual([]);
  });

  it('binds form fields correctly', async () => {
    const { component, getByLabelText, getByText } = render(GrowthRecordForm, {
      props: { record: mockRecord }
    });

    const dateInput = getByLabelText('日期');
    const weightInput = getByLabelText('体重 (kg)');
    const heightInput = getByLabelText('身高 (cm)');
    const notesInput = getByLabelText('备注');

    fireEvent.input(dateInput, { target: { value: '2025-02-01' } });
    fireEvent.input(weightInput, { target: { value: '5.0' } });
    fireEvent.input(heightInput, { target: { value: '30' } });
    fireEvent.input(notesInput, { target: { value: 'Updated notes' } });

    // 通过提交事件验证表单数据
    const mockHandler = vi.fn();
    component.$on('save', mockHandler);
    
    fireEvent.click(getByText('保存'));
    expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({
      detail: {
        id: '1',
        record: expect.objectContaining({
          date: '2025-02-01',
          weight: 5.0,
          height: 30,
          notes: 'Updated notes'
        })
      }
    }));
  });

  it('applies correct CSS classes', () => {
    const { container } = render(GrowthRecordForm);

    expect(container.querySelector('.growth-record-form')).toBeInTheDocument();
    expect(container.querySelector('.growth-record-form__field')).toBeInTheDocument();
    expect(container.querySelector('.growth-record-form__actions')).toBeInTheDocument();
  });

  it('handles multiple validation errors', async () => {
    const { component, container } = render(GrowthRecordForm, {
      props: { 
        record: { 
          ...mockRecord, 
          date: '',
          weight: -1,
          height: -1 
        } 
      }
    });

    const mockHandler = vi.fn();
    component.$on('error', mockHandler);

    const form = container.querySelector('form');
    if (!form) {
      throw new Error('Form not found');
    }

    fireEvent.submit(form);
    
    expect(mockHandler).toHaveBeenCalled();
    const errorMessage = mockHandler.mock.calls[0][0].detail;
    expect(errorMessage).toContain('日期不能为空');
    expect(errorMessage).toContain('体重必须大于0');
    expect(errorMessage).toContain('身高必须大于0');
  });

  it('handles single field validation scenarios', async () => {
    const testCases = [
      { 
        field: 'date', 
        value: '', 
        shouldError: true,
        error: '日期不能为空' 
      },
      { 
        field: 'weight', 
        value: 0, 
        shouldError: true,
        error: '体重必须大于0' 
      },
      { 
        field: 'weight', 
        value: -1, 
        shouldError: true,
        error: '体重必须大于0' 
      },
      { 
        field: 'weight', 
        value: undefined, 
        shouldError: false
      },
      { 
        field: 'height', 
        value: 0, 
        shouldError: true,
        error: '身高必须大于0' 
      },
      { 
        field: 'height', 
        value: -0.1, 
        shouldError: true,
        error: '身高必须大于0' 
      },
      { 
        field: 'height', 
        value: undefined, 
        shouldError: false
      }
    ];

    for (const testCase of testCases) {
      const { component, container } = render(GrowthRecordForm, {
        props: { 
          record: { 
            ...mockRecord,
            [testCase.field]: testCase.value
          } 
        }
      });

      const mockHandler = vi.fn();
      component.$on('error', mockHandler);

      const form = container.querySelector('form');
      if (!form) {
        throw new Error('Form not found');
      }

      fireEvent.submit(form);
      
      if (testCase.shouldError) {
        expect(mockHandler).toHaveBeenCalled();
        const errorMessage = mockHandler.mock.calls[0][0].detail;
        expect(errorMessage).toContain(testCase.error);
      } else {
        expect(mockHandler).not.toHaveBeenCalled();
      }
    }
  });

  it('handles multiple field validation scenarios', async () => {
    const { component, container } = render(GrowthRecordForm, {
      props: { 
        record: { 
          ...mockRecord,
          date: '',
          weight: -1,
          height: -1
        } 
      }
    });

    const mockHandler = vi.fn();
    component.$on('error', mockHandler);

    const form = container.querySelector('form');
    if (!form) {
      throw new Error('Form not found');
    }

    fireEvent.submit(form);
    
    expect(mockHandler).toHaveBeenCalled();
    const errorMessage = mockHandler.mock.calls[0][0].detail;
    expect(errorMessage).toContain('日期不能为空');
    expect(errorMessage).toContain('体重必须大于0');
    expect(errorMessage).toContain('身高必须大于0');
  });
});
