<script lang="ts">
  import { page } from '$app/stores';
  export let data;
</script>

<svelte:head>
  <title>CATalogue - 猫咪详情</title>
</svelte:head>

<div class="container">
  <h1>猫咪详情</h1>
  <p>猫咪ID: {data.params.id}</p>
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }
</style>
