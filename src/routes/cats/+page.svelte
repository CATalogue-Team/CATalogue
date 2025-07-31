<script lang="ts">
  import { page } from '$app/stores';
  import CatProfile from '$lib/components/CatProfile.svelte';
  import { catStore, fetchCats } from '$lib/stores/cat.store';
  import { onMount } from 'svelte';

  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      await fetchCats();
      loading = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error';
      loading = false;
    }
  });

  $: cats = Array.from($catStore.cats.values());
</script>

<svelte:head>
  <title>CATalogue - 猫咪档案</title>
</svelte:head>

<div class="container">
  <h1>猫咪档案</h1>
  
  {#if loading}
    <p>加载中...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    {#each cats as cat}
      <CatProfile {cat} />
    {/each}
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
