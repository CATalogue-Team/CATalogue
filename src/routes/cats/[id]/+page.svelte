<script lang="ts">
  
  import CatProfileComponent from '../../../lib/components/CatProfile.svelte';
  import GrowthRecordComponent from '../../../lib/components/GrowthRecord/GrowthRecord.svelte';
  import { catStore, fetchCat } from '../../../lib/stores/cat.store.ts';
  import { onMount } from 'svelte';
  import type { CatState, Cat } from '../../../lib/stores/cat.store.ts';

  export let data;
  let unsubscribe: () => void;
  
  // 声明响应式变量
  let cat: Cat | undefined;
  let loading = true;
  let error: string | null = null;
  
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
          <GrowthRecordComponent record={record} editable={true} />
        {/each}
      </div>
    {:else}
      <p>暂无成长记录</p>
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
</style>
