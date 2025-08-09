<script lang="ts">
  import '../app.css';
  import { authStore, login, logout, initializeAuth } from '../lib/stores/auth.store.ts';
  import { onMount } from 'svelte';

  onMount(async () => {
    await initializeAuth();
  });

  function handleLogout() {
    logout();
  }
</script>

<div class="app-container">
  <nav>
    <a href="/">首页</a>
    <a href="/cats">猫咪档案</a>
    <a href="/community">社区</a>
    
    {#if $authStore.isAuthenticated}
      <span class="user-info">
        欢迎，{$authStore.user?.username}
        <button on:click={handleLogout} class="logout-btn">登出</button>
      </span>
    {:else}
      <div class="auth-links">
        <a href="/login">登录</a>
        <a href="/register">注册</a>
      </div>
    {/if}
  </nav>

  <slot />
</div>

<style>
  .app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  nav {
    background: #333;
    padding: 1rem;
  }
  
  nav a {
    color: white;
    margin-right: 1rem;
    text-decoration: none;
  }
  
  nav a:hover {
    text-decoration: underline;
  }
</style>
