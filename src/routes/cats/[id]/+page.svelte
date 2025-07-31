<script lang="ts">
  import { page } from '$app/stores';
  import CatProfile from '$lib/components/CatProfile.svelte';
  import { catStore, fetchCat } from '$lib/stores/cat.store';
  import { onMount } from 'svelte';

  export let data;
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      await fetchCat(data.params.id);
      loading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
      loading = false;
    }
  });

  $: cat = $catStore.cats.get(data.params.id);
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
    <CatProfile {cat} />
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
