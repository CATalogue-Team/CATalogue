<script lang="ts">
  import { onMount } from 'svelte';
  import { postStore } from '../../lib/stores/post.store.ts';
  
  $: loading = $postStore.loading;
  $: error = $postStore.error;
  $: posts = $postStore.posts;
  
  onMount(() => {
    postStore.fetchPosts();
  });
</script>

<div class="community-page">
  <h1>社区论坛</h1>
  
  {#if loading}
    <p>加载中...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if posts.length > 0}
    <div class="post-list">
      {#each posts as post (post.id)}
        <a href={`/community/${post.id}`} class="post-item">
          <h3>{post.title}</h3>
          <p>作者ID: {post.author_id}</p>
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
