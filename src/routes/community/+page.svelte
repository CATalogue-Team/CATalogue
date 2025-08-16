<script lang="ts">
  import { onMount } from 'svelte';
  import { postStore } from '../../lib/stores/post.store.ts';
  import { authStore, initializeAuth } from '../../lib/stores/auth.store.ts';
  
  $: loading = $postStore.loading;
  $: error = $postStore.error;
  $: posts = $postStore.posts;
  $: isAuthenticated = $authStore.isAuthenticated;
  
  onMount(() => {
    initializeAuth().then(() => {
      postStore.fetchPosts();
    });
  });

  async function handleCreatePost() {
    try {
      const title = prompt('请输入帖子标题');
      if (!title) return;
      
      const content = prompt('请输入帖子内容');
      if (!content) return;

      const user = $authStore.user;
      if (!user) throw new Error('用户未登录');

      const success = await postStore.createPost({ 
        title, 
        content,
        author_name: user.username
      });
      if (success) {
        alert('帖子创建成功');
      } else {
        alert('创建帖子失败');
      }
    } catch (err) {
      console.error('创建帖子出错:', err);
      alert('创建帖子时出错');
    }
  }
</script>

<div class="community-page">
  <div class="header">
    <h1>社区论坛</h1>
    {#if isAuthenticated}
      <button on:click={handleCreatePost} class="create-btn">创建帖子</button>
    {/if}
  </div>
  
  {#if loading}
    <p>加载中...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if posts.length > 0}
    <div class="post-list">
      {#each posts as post (post.id)}
        <a href={`/community/${post.id}`} class="post-item">
          <h3>{post.title}</h3>
          <p>作者: {post.author_name}</p>
          <p>发布于: {new Date(post.created_at).toLocaleString()}</p>
        </a>
      {/each}
    </div>
  {:else}
    <p>暂无帖子</p>
  {/if}
</div>

<style>
  .community-page {
    padding: 1rem;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .create-btn {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .create-btn:hover {
    background: #0069d9;
  }

  .post-list {
    margin-top: 1rem;
  }

  .post-item {
    display: block;
    padding: 1rem;
    border: 1px solid #eee;
    margin-bottom: 1rem;
    text-decoration: none;
    color: inherit;
  }
</style>
