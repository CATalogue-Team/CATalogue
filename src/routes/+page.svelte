<script lang="ts">
  import { goto } from '$app/navigation';
  import { authStore, type AuthState } from '../lib/stores/auth.store.ts';

  $: isLoggedIn = $authStore.isAuthenticated;

  function navigateTo(path: string) {
    goto(path);
  }
</script>

<svelte:head>
  <title>CATalogue - 猫咪档案管理系统</title>
</svelte:head>

<div class="container">
  <h1>欢迎来到CATalogue</h1>
  <p class="subtitle">专业的猫咪档案管理与社区平台</p>

  {#if isLoggedIn}
    <div class="actions">
      <button on:click={() => navigateTo('/cats')}>查看猫咪档案</button>
      <button on:click={() => navigateTo('/community')}>进入社区</button>
    </div>
  {:else}
    <div class="actions">
      <button on:click={() => navigateTo('/login')}>登录</button>
      <button on:click={() => navigateTo('/register')}>注册</button>
    </div>
  {/if}

  <div class="features">
    <div class="feature-card">
      <h3>猫咪档案管理</h3>
      <p>记录猫咪的详细信息、成长轨迹和健康数据</p>
    </div>
    <div class="feature-card">
      <h3>社区交流</h3>
      <p>与其他猫主人分享经验和知识</p>
    </div>
  </div>
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
  }

  h1 {
    color: #ff3e00;
    margin-bottom: 0.5rem;
  }

  .subtitle {
    color: #666;
    margin-bottom: 2rem;
  }

  .actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin: 2rem 0;
  }

  .actions button {
    padding: 0.75rem 1.5rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .actions button:hover {
    background-color: #0069d9;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 3rem;
  }

  .feature-card {
    padding: 1.5rem;
    border: 1px solid #eee;
    border-radius: 8px;
    text-align: left;
  }

  .feature-card h3 {
    color: #333;
    margin-bottom: 0.5rem;
  }
</style>
