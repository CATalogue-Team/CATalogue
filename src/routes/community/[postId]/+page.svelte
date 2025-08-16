<script lang="ts">
  import { page } from '$app/stores';
  import { writable } from 'svelte/store';
  import { onMount } from 'svelte';
  import { postStore, type Post } from '../../../lib/stores/post.store.ts';
  import { authStore, initializeAuth } from '../../../lib/stores/auth.store.ts';
  
  let commentContent = '';
  
  // 获取路由参数
  export let data: { postId: string };

  const post = writable<Post | null>(null);
  const loading = writable(false);
  const error = writable<string | null>(null);

  onMount(() => {
    // 初始化auth
    initializeAuth().then(() => {
      postStore.fetchPost(data.postId);
    });
    
    // 订阅postStore变化
    const unsubscribe = postStore.subscribe(store => {
      post.set(store.currentPost);
      loading.set(store.loading);
      error.set(store.error);
    });
    
    return unsubscribe;
  });

  async function handleAddComment() {
    try {
      const success = await postStore.addComment(data.postId, {
        content: commentContent,
        author_name: $authStore.user?.username || '匿名'
      });
      if (success) {
        commentContent = '';
        await postStore.fetchPost(data.postId);
      }
    } catch (err) {
      console.error('添加评论失败:', err);
    }
  }

  async function handleDeleteComment(commentId: string) {
    try {
      const success = await postStore.deleteComment(data.postId, commentId);
      if (success) {
        await postStore.fetchPost(data.postId);
      }
    } catch (err) {
      console.error('删除评论失败:', err);
    }
  }
</script>

{#if $error}
  <div class="error">{$error}</div>
{:else if $loading}
  <div class="loading">加载中...</div>
{:else if $post}
  <article class="post-detail">
    <h1>{$post.title}</h1>
    <div class="meta">
      <span>作者: {$post.author_name}</span>
      <span>发布时间: {$post.created_at}</span>
    </div>
    
    <div class="content">
      {$post.content}
    </div>

    <section class="comments">
      <h2>评论</h2>
      {#if $authStore.isAuthenticated}
        <form on:submit|preventDefault={handleAddComment} class="comment-form">
          <textarea bind:value={commentContent} placeholder="写下你的评论..." required />
          <button type="submit">提交评论</button>
        </form>
      {:else}
        <p class="login-prompt">请<a href="/login">登录</a>后发表评论</p>
      {/if}

      {#if $post.comments && $post.comments.length > 0}
        {#each $post.comments as comment}
          <div class="comment">
            <div class="comment-header">
              <span>{comment.author_name}</span>
              {#if $authStore.user?.id === comment.author_id}
                <button on:click={() => handleDeleteComment(comment.id)} class="delete-btn">删除</button>
              {/if}
            </div>
            <div class="comment-content">
              {comment.content}
            </div>
            <div class="comment-time">
              {comment.created_at}
            </div>
          </div>
        {/each}
      {:else}
        <p>暂无评论</p>
      {/if}
    </section>
  </article>
{:else}
  <p>帖子不存在</p>
{/if}

<style>
  .post-detail {
    padding: 1rem;
  }

  .meta {
    color: #666;
    margin: 0.5rem 0;
    font-size: 0.9rem;
  }

  .content {
    margin: 1rem 0;
    line-height: 1.6;
  }

  .comments {
    margin-top: 2rem;
    border-top: 1px solid #eee;
    padding-top: 1rem;
  }

  .comment {
    margin: 1rem 0;
    padding: 1rem;
    border: 1px solid #eee;
    border-radius: 4px;
  }

  .comment-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .comment-header img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
  }

  .comment-time {
    color: #999;
    font-size: 0.8rem;
    margin-top: 0.5rem;
  }
</style>
