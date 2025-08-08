<script lang="ts">
  import { page } from '$app/stores';
  import CatProfile from '$lib/components/CatProfile.svelte';
  import * as catStoreModule from '$lib/stores/cat.store';
  import { onMount } from 'svelte';

  const { catStore, fetchCats } = catStoreModule;

  onMount(async () => {
    await fetchCats();
  });

  $: cats = Array.from($catStore.cats.values());
  $: loading = $catStore.loading;
  $: error = $catStore.error;
</script>

<svelte:head>
  <title>CATalogue - 猫咪档案</title>
</svelte:head>

<div class="container" data-testid="cats-container">
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
