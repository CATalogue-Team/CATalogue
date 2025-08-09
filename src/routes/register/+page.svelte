<script lang="ts">
  import { goto } from '$app/navigation';
  import { authStore , login} from '$lib/stores/auth.store.ts';

  let username = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let fullName = '';
  let error = '';
  let loading = false;

  async function handleRegister() {
    if (password !== confirmPassword) {
      error = '两次输入的密码不一致';
      return;
    }

    if (!username || !password || !email) {
      error = '请填写所有必填字段';
      return;
    }

    loading = true;
    error = '';

    try {
      const response = await fetch('/api/v1/users/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password,
          full_name: fullName
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || '注册失败');
      }

      // 注册成功后自动登录
      const loginResponse = await fetch('/api/v1/users/login', {
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

      if (!loginResponse.ok) {
        throw new Error('自动登录失败，请手动登录');
      }

      const { access_token } = await loginResponse.json();
      login(access_token);
      goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : '注册失败';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>CATalogue - 注册</title>
</svelte:head>

<div class="register-container">
  <h1>注册</h1>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}

  <form on:submit|preventDefault={handleRegister}>
    <div class="form-group">
      <label for="username">用户名*</label>
      <input 
        id="username" 
        type="text" 
        bind:value={username} 
        disabled={loading}
      />
    </div>

    <div class="form-group">
      <label for="email">邮箱*</label>
      <input 
        id="email" 
        type="email" 
        bind:value={email} 
        disabled={loading}
      />
    </div>

    <div class="form-group">
      <label for="fullName">全名</label>
      <input 
        id="fullName" 
        type="text" 
        bind:value={fullName} 
        disabled={loading}
      />
    </div>

    <div class="form-group">
      <label for="password">密码*</label>
      <input 
        id="password" 
        type="password" 
        bind:value={password} 
        disabled={loading}
      />
    </div>

    <div class="form-group">
      <label for="confirmPassword">确认密码*</label>
      <input 
        id="confirmPassword" 
        type="password" 
        bind:value={confirmPassword} 
        disabled={loading}
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? '注册中...' : '注册'}
    </button>
  </form>

  <p class="login-link">
    已有账号？<a href="/login">立即登录</a>
  </p>
</div>

<style>
  .register-container {
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

  label:after {
    content: '*';
    color: red;
    margin-left: 0.2rem;
    display: none;
  }

  label[for="username"]:after,
  label[for="email"]:after,
  label[for="password"]:after,
  label[for="confirmPassword"]:after {
    display: inline;
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

  .login-link {
    text-align: center;
    margin-top: 1rem;
  }
</style>
