<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    upload: File[];
    error: string;
  }>();

  export let accept = '*';
  export let multiple = false;
  export let maxSize = 5 * 1024 * 1024; // 5MB
  export let dataTestid = '';

  let files: File[] = [];
  let previews: string[] = [];
  let error = '';

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;

    const newFiles = Array.from(input.files);
    
    // 检查文件大小
    const oversizedFiles = newFiles.filter(file => file.size > maxSize);
    if (oversizedFiles.length > 0) {
      error = `文件大小不能超过${maxSize / 1024 / 1024}MB`;
      dispatch('error', error);
      return;
    }

    files = multiple ? [...files, ...newFiles] : newFiles;
    error = '';

    // 生成预览
    previews = [];
    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previews = [...previews, e.target?.result as string];
        };
        reader.readAsDataURL(file);
      }
    });

    dispatch('upload', files);
  }

  function removeFile(index: number) {
    files = files.filter((_, i) => i !== index);
    previews = previews.filter((_, i) => i !== index);
    dispatch('upload', files);
  }
</script>

<div class="file-upload" data-testid={dataTestid}>
  <input
    type="file"
    {accept}
    {multiple}
    on:change={handleFileChange}
    id="fileInput"
    style="display: none;"
  />

  <button type="button" on:click={() => document.getElementById('fileInput')?.click()}>
    选择文件
  </button>

  {#if error}
    <div class="file-upload__error">{error}</div>
  {/if}

  <div class="file-upload__previews">
    {#each previews as preview, index}
      <div class="file-upload__preview">
        <img src={preview} alt="预览" />
        <button type="button" on:click={() => removeFile(index)}>删除</button>
      </div>
    {/each}
  </div>
</div>

<style>
  .file-upload {
    margin: 1rem 0;
  }

  .file-upload button {
    padding: 0.5rem 1rem;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
  }

  .file-upload__error {
    color: red;
    margin: 0.5rem 0;
  }

  .file-upload__previews {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
  }

  .file-upload__preview {
    position: relative;
    width: 100px;
    height: 100px;
  }

  .file-upload__preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
  }

  .file-upload__preview button {
    position: absolute;
    top: 0;
    right: 0;
    padding: 0.2rem;
    background-color: rgba(255, 0, 0, 0.7);
    color: white;
    border: none;
    border-radius: 0 4px 0 4px;
  }
</style>
