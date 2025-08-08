<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
</script>

<svelte:head>
  <title>CATalogue - 猫咪档案管理系统</title>
</svelte:head>

<div class="container">
  <h1>欢迎来到CATalogue</h1>
  <p>猫咪档案管理与社区平台</p>
  <button on:click={() => goto('/temp-test')}>转到 GrowthRecord 组件测试页</button>
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }
  h1 {
    color: #ff3e00;
  }
</style>
