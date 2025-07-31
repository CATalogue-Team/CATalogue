<script lang="ts">
<<<<<<< HEAD
  import { createEventDispatcher } from 'svelte';

=======
>>>>>>> d481a85 (feat: 添加PWA支持配置)
  export let cat: {
    id: string;
    name: string;
    age: number;
    breed?: string;
    photos: string[];
  };
<<<<<<< HEAD

  export let editable = false;

  const dispatch = createEventDispatcher<{
    photoUpload: File[];
    edit: { id: string };
    delete: { id: string };
  }>();

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      dispatch('photoUpload', Array.from(input.files));
    }
  }
</script>

<div class="cat-profile">
  <div class="header">
    <h2>{cat.name}</h2>
    {#if editable}
      <div class="actions">
        <button on:click={() => dispatch('edit', { id: cat.id })}>编辑</button>
        <button on:click={() => dispatch('delete', { id: cat.id })}>删除</button>
      </div>
    {/if}
  </div>

=======
</script>

<div class="cat-profile">
  <h2>{cat.name}</h2>
>>>>>>> d481a85 (feat: 添加PWA支持配置)
  <p>年龄: {cat.age}岁</p>
  {#if cat.breed}
    <p>品种: {cat.breed}</p>
  {/if}
<<<<<<< HEAD

  {#if cat.photos.length > 0}
    <div class="photos">
      {#each cat.photos as photo}
        <img src={photo} alt={`${cat.name}的照片`} />
      {/each}
    </div>
  {/if}

  {#if editable}
    <input
      type="file"
      accept="image/*"
      multiple
      on:change={handleFileChange}
    />
  {/if}
=======
>>>>>>> d481a85 (feat: 添加PWA支持配置)
</div>

<style>
  .cat-profile {
    padding: 1rem;
    border: 1px solid #ddd;
    margin-bottom: 1rem;
    border-radius: 4px;
  }
<<<<<<< HEAD

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .actions button {
    margin-left: 0.5rem;
  }

  .photos {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
  }

  img {
    max-width: 100px;
    max-height: 100px;
    object-fit: cover;
  }
=======
>>>>>>> d481a85 (feat: 添加PWA支持配置)
</style>
