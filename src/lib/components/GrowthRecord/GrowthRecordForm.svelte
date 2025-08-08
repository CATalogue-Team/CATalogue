<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { GrowthRecord } from '../../types.js';
  import FileUpload from '../FileUpload.svelte';
  
  const dispatch = createEventDispatcher<{
    save: { id: string; record: Partial<GrowthRecord> };
    cancel: void;
    error: string;
    photoUpload: File[];
  }>();

  export let record: GrowthRecord | null = null;
  export let saveError = '';

  let formData: Partial<GrowthRecord> = {
    date: '',
    weight: undefined,
    height: undefined,
    notes: '',
    photos: []
  };

  // 初始化表单数据
  $: {
    if (record) {
      formData = {
        date: record.date,
        weight: record.weight,
        height: record.height,
        notes: record.notes,
        photos: [...record.photos]
      };
    }
  }

  function handleSubmit() {
    // 收集所有验证错误
    const errors = [];
    if (!formData.date) {
      errors.push('日期不能为空');
    }
    if (formData.weight !== undefined && formData.weight <= 0) {
      errors.push('体重必须大于0');
    }
    if (formData.height !== undefined && formData.height <= 0) {
      errors.push('身高必须大于0');
    }

    if (errors.length > 0) {
      dispatch('error', errors.join(','));
      return;
    }

    const id = record?.id || crypto.randomUUID();
    dispatch('save', { id, record: formData });
  }

  function handleCancel() {
    dispatch('cancel');
  }

  function handlePhotoUpload(event: CustomEvent<File[]>) {
    dispatch('photoUpload', event.detail);
  }
</script>

<div class="growth-record-form">
  {#if saveError}
    <div class="growth-record-form__error">{saveError}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit}>
    <div class="growth-record-form__field">
      <label for="date">日期</label>
      <input
        id="date"
        type="date"
        bind:value={formData.date}
        required
      />
    </div>

    <div class="growth-record-form__field">
      <label for="weight">体重 (kg)</label>
      <input
        id="weight"
        type="number"
        step="0.1"
        min="0"
        bind:value={formData.weight}
      />
    </div>

    <div class="growth-record-form__field">
      <label for="height">身高 (cm)</label>
      <input
        id="height"
        type="number"
        step="0.1"
        min="0"
        bind:value={formData.height}
      />
    </div>

    <div class="growth-record-form__field">
      <label for="notes">备注</label>
      <textarea
        id="notes"
        bind:value={formData.notes}
      />
    </div>

    <FileUpload 
      accept="image/*" 
      multiple
      maxSize={5 * 1024 * 1024} 
      on:upload={handlePhotoUpload}
      dataTestid="file-upload"
    />

    <div class="growth-record-form__actions">
      <button type="button" on:click={handleCancel}>取消</button>
      <button type="submit">保存</button>
    </div>
  </form>
</div>

<style>
  .growth-record-form {
    padding: 1rem;
  }

  .growth-record-form__error {
    color: red;
    margin-bottom: 1rem;
  }

  .growth-record-form__field {
    margin-bottom: 1rem;
  }

  .growth-record-form__field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
  }

  .growth-record-form__field input,
  .growth-record-form__field textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .growth-record-form__actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1rem;
  }

  .growth-record-form__actions button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .growth-record-form__actions button[type="submit"] {
    background-color: #007bff;
    color: white;
  }
</style>
