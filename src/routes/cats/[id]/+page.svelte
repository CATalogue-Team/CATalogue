<script lang="ts">
  import CatProfileComponent from '../../../lib/components/CatProfile.svelte';
  import GrowthRecordComponent from '../../../lib/components/GrowthRecord/GrowthRecord.svelte';
  import GrowthRecordForm from '../../../lib/components/GrowthRecord/GrowthRecordForm.svelte';
  import { 
    catStore, 
    fetchCat,
    createGrowthRecord,
    updateGrowthRecord,
    deleteGrowthRecord,
    uploadCatPhotos
  } from '../../../lib/stores/cat.store.ts';
  import { onMount } from 'svelte';
  import type { CatState, Cat } from '../../../lib/stores/cat.store.ts';
  import type { GrowthRecord } from '../../../lib/types.js';

  export let data;
  let unsubscribe: () => void;
  
  // 声明响应式变量
  let cat: Cat | undefined;
  let loading = true;
  let error: string | null = null;
  let showForm = false;
  let formError = '';
  
  // 使用store自动更新变量
  $: {
    cat = $catStore.cats.get(data.params.id);
    loading = $catStore.loading;
    error = $catStore.error;
  }
  
  onMount(() => {
    fetchCat(data.params.id).catch(err => {
      console.error('Failed to fetch cat:', err);
    });
    
    return () => {
    };
  });

  async function handleSaveRecord(event: CustomEvent<{ id: string; record: Partial<GrowthRecord> }>) {
    const { id, record } = event.detail;
    try {
      if (id.startsWith('new-')) {
        // 创建新记录
        await createGrowthRecord(data.params.id, record as Omit<GrowthRecord, 'id'>);
      } else {
        // 更新现有记录
        await updateGrowthRecord(data.params.id, id, record);
      }
      showForm = false;
    } catch (err) {
      formError = err instanceof Error ? err.message : '保存失败';
    }
  }

  async function handlePhotoUpload(event: CustomEvent<File[]>) {
    if (!cat) return;
    try {
      await uploadCatPhotos(cat.id, event.detail);
    } catch (err) {
      formError = err instanceof Error ? err.message : '照片上传失败';
    }
  }

  async function handleDeleteRecord(recordId: string) {
    if (!cat) return;
    try {
      await deleteGrowthRecord(cat.id, recordId);
    } catch (err) {
      formError = err instanceof Error ? err.message : '删除失败';
    }
  }
</script>

<svelte:head>
  <title>CATalogue - 猫咪详情</title>
</svelte:head>

<div class="container">
  <h1>猫咪详情</h1>
  
  {#if loading}
    <p>加载中...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if !cat}
    <p>未找到猫咪信息</p>
  {:else}
    <CatProfileComponent cat={cat} />
    <h2>成长记录</h2>
    {#if cat.growthRecords && cat.growthRecords.length > 0}
      <div class="growth-records">
        {#each cat.growthRecords as record (record.id)}
          <GrowthRecordComponent 
            record={record} 
            editable={true}
            on:delete={() => handleDeleteRecord(record.id)}
          />
        {/each}
      </div>
    {:else}
      <p>暂无成长记录</p>
    {/if}

    {#if showForm}
      <div class="form-container">
        <GrowthRecordForm
          on:save={handleSaveRecord}
          on:photoUpload={handlePhotoUpload}
          on:cancel={() => showForm = false}
          on:error={(e) => formError = e.detail}
          saveError={formError}
        />
      </div>
    {:else}
      <button on:click={() => showForm = true} class="add-record-btn">
        添加成长记录
      </button>
    {/if}
  {/if}
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .error {
    color: red;
  }

  .form-container {
    margin-top: 2rem;
    padding: 1rem;
    border: 1px solid #eee;
    border-radius: 4px;
  }

  .add-record-btn {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .add-record-btn:hover {
    background-color: #0069d9;
  }
</style>
