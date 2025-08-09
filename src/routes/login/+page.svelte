<script lang="ts">
  import { goto } from '$app/navigation';
  import { authStore , login} from '$lib/stores/auth.store.ts';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    if (!username || !password) {
      error = '请输入用户名和密码';
      return;
    }

    loading = true;
    error = '';
    
    try {
      const response = await fetch('/api/v1/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
          grant_type: 'password',
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || '登录失败');
      }

      const { access_token } = await response.json();
      login(access_token);
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : '登录失败';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>CATalogue - 登录</title>
</svelte:head>

<div class="login-container">
  <h1>登录</h1>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}

  <form on:submit|preventDefault={handleLogin}>
    <div class="form-group">
      <label for="username">用户名</label>
      <input 
        id="username" 
        type="text" 
        bind:value={username} 
        disabled={loading}
      />
    </div>

    <div class="form-group">
      <label for="password">密码</label>
      <input 
        id="password" 
        type="password" 
        bind:value={password} 
        disabled={loading}
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? '登录中...' : '登录'}
    </button>
  </form>

  <p class="register-link">
    还没有账号？<a href="/register">立即注册</a>
  </p>
</div>

<style>
  .login-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    border: 1px solid #eee;
    border-radius: 8px;
  }

  h1 {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  button {
    width: 100%;
    padding: 0.75rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1rem;
  }

  button:hover {
    background-color: #0069d9;
  }

  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .error {
    color: red;
    margin-bottom: 1rem;
  }

  .register-link {
    text-align: center;
    margin-top: 1rem;
  }
</style>
