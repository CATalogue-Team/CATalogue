import { render } from '@testing-library/svelte';
import FileUpload from '../../../src/lib/components/FileUpload.svelte';
import { vi } from 'vitest';

// Mock FileReader
class MockFileReader {
  static readonly EMPTY = 0;
  static readonly LOADING = 1;
  static readonly DONE = 2;

  result: string | ArrayBuffer | null = '';
  error: DOMException | null = null;
  readyState = MockFileReader.DONE;
  onload: ((this: any, ev: any) => any) | null = null;
  onerror: ((this: any, ev: any) => any) | null = null;
  onabort: ((this: any, ev: any) => any) | null = null;
  onloadstart: ((this: any, ev: any) => any) | null = null;
  onloadend: ((this: any, ev: any) => any) | null = null;
  onprogress: ((this: any, ev: any) => any) | null = null;
  
  readAsDataURL() {
    this.result = 'data:image/png;base64,mock';
    if (this.onload) {
      this.onload(new ProgressEvent('load'));
    }
  }

  abort() {
    this.readyState = MockFileReader.DONE;
    if (this.onabort) {
      this.onabort(new ProgressEvent('abort'));
    }
  }
  readAsArrayBuffer() {
    this.result = new ArrayBuffer(0);
    if (this.onload) {
      this.onload(new ProgressEvent('load'));
    }
  }
  readAsBinaryString() {
    this.result = '0110100001100101011011000110110001101111'; // "hello" in binary
    if (this.onload) {
      this.onload(new ProgressEvent('load'));
    }
  }
  readAsText() {
    this.result = 'text content';
    if (this.onload) {
      this.onload(new ProgressEvent('load'));
    }
  }

  // 简化的事件方法
  addEventListener(type: string, listener: any): void {
    // Mock实现，测试中不需要实际功能
  }
  removeEventListener(type: string, listener: any): void {
    // Mock实现，测试中不需要实际功能
  }
  dispatchEvent(event: any): boolean { 
    // Mock实现，测试中不需要实际功能
    return true; 
  }
}

describe('FileUpload Component', () => {
  beforeAll(() => {
    // 模拟全局API
    vi.stubGlobal('FileReader', MockFileReader);
  });

  afterAll(() => {
    vi.unstubAllGlobals();
  });

  it('should dispatch upload event with selected file', async () => {
    const mockDispatch = vi.fn();
    const { container, getByText, component } = render(FileUpload);
    component.$on('upload', mockDispatch);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['test'], 'test.png', { type: 'image/png' });
    
    // 直接触发 change 事件
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Wait for FileReader
    await new Promise(resolve => setTimeout(resolve, 10));
    
    expect(mockDispatch).toHaveBeenCalledWith(expect.objectContaining({
      detail: expect.arrayContaining([file])
    }));
  });

  it('should dispatch error event when file exceeds max size', async () => {
    const mockDispatch = vi.fn();
    const { container, getByText, component } = render(FileUpload, { props: { maxSize: 1 } });
    component.$on('error', mockDispatch);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['test'], 'test.png', { type: 'image/png' });
    
    // 直接触发 change 事件
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    expect(mockDispatch).toHaveBeenCalledWith(expect.objectContaining({
      detail: '文件大小不能超过9.5367431640625e-7MB'
    }));
  });

  it('should support multiple file upload', async () => {
    const mockDispatch = vi.fn();
    const { container, getByText, component } = render(FileUpload, { props: { multiple: true } });
    component.$on('upload', mockDispatch);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const files = [
      new File(['test1'], 'test1.png', { type: 'image/png' }),
      new File(['test2'], 'test2.png', { type: 'image/png' })
    ];
    
    // 直接触发 change 事件
    Object.defineProperty(input, 'files', {
      value: files
    });
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Wait for FileReader
    await new Promise(resolve => setTimeout(resolve, 10));
    
    expect(mockDispatch).toHaveBeenCalledWith(expect.objectContaining({
      detail: expect.arrayContaining(files)
    }));
  });

  it('should generate preview for image files', async () => {
    const { container, getByText, findByAltText } = render(FileUpload);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['test'], 'test.png', { type: 'image/png' });
    
    // 直接触发 change 事件
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    expect(await findByAltText('预览')).toBeInTheDocument();
  });

  it('should remove file when delete button clicked', async () => {
    const mockDispatch = vi.fn();
    const { container, getByText, findByText, component } = render(FileUpload);
    component.$on('upload', mockDispatch);
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['test'], 'test.png', { type: 'image/png' });
    
    // 直接触发 change 事件
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    const deleteButton = await findByText('删除');
    deleteButton.click();
    
    expect(mockDispatch).toHaveBeenCalledWith(expect.objectContaining({
      detail: []
    }));
  });
});
