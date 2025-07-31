<script context="module" lang="ts">
  interface User {
    id: string;
    name: string;
  }

  interface Post {
    id: string;
    title: string;
    author: User;
  }

  export interface PageData {
    posts: Post[];
  }
</script>

<script lang="ts">
  import { writable } from 'svelte/store';
  export let data: PageData;
  const posts = writable<Post[]>(data?.posts || []);
</script>

<div class="community-page">
  <h1>社区论坛</h1>
  
  {#if $posts.length > 0}
    <div class="post-list">
      {#each $posts as post (post.id)}
        <a href={`/community/${post.id}`} class="post-item">
          <h3>{post.title}</h3>
          <p>作者: {post.author.name}</p>
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
