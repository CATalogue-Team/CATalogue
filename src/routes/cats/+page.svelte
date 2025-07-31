<script lang="ts">
  import { page } from '$app/stores';
  import CatProfile from '$lib/components/CatProfile.svelte';

  const cats = [
    {
      id: '1',
      name: '小花',
      age: 2,
      breed: '英国短毛猫',
      photos: []
    },
    {
      id: '2',
      name: '小黑',
      age: 3,
      photos: []
    }
  ];
</script>

<svelte:head>
  <title>CATalogue - 猫咪档案</title>
</svelte:head>

<div class="container">
  <h1>猫咪档案</h1>
  
  {#each cats as cat}
    <CatProfile {cat} />
  {/each}
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }
</style>
