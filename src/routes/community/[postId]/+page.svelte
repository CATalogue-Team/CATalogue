<script lang="ts">
  import { page } from '$app/stores';
  import { writable } from 'svelte/store';

  interface User {
    id: string;
    name: string;
    avatar?: string;
  }

  interface Comment {
    id: string;
    content: string;
    author: User;
    createdAt: string;
  }

  interface Post {
    id: string;
    title: string;
    content: string;
    author: User;
    createdAt: string;
    comments: Comment[];
  }

  // 获取路由参数
  export let data: { postId: string };

  // TODO: 实现帖子数据获取
  const post = writable<Post | null>(null);
  const loading = writable(false);
  const error = writable<string | null>(null);
</script>

{#if $error}
  <div class="error">{$error}</div>
{:else if $loading}
  <div class="loading">加载中...</div>
{:else if $post}
  <article class="post-detail">
    <h1>{$post.title}</h1>
    <div class="meta">
      <span>作者: {$post.author.name}</span>
      <span>发布时间: {$post.createdAt}</span>
    </div>
    
    <div class="content">
      {$post.content}
    </div>

    <section class="comments">
      <h2>评论</h2>
      {#if $post.comments.length > 0}
        {#each $post.comments as comment (comment.id)}
          <div class="comment">
            <div class="comment-header">
              {#if comment.author.avatar}
                <img src={comment.author.avatar} alt={comment.author.name} />
              {/if}
              <span>{comment.author.name}</span>
            </div>
            <div class="comment-content">
              {comment.content}
            </div>
            <div class="comment-time">
              {comment.createdAt}
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
