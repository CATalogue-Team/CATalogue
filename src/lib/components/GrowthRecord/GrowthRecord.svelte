<script lang="ts">
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  import type { GrowthRecord } from '../../types.js';
  import GrowthRecordForm from './GrowthRecordForm.svelte';

  const dispatch = createEventDispatcher<{
    add: { id: string; record: Partial<GrowthRecord> };
    edit: { id: string; record: Partial<GrowthRecord> };
    delete: { id: string };
    photoUpload: File[];
  }>();
  export let record: GrowthRecord | null = null;
  export let editable = false;

  let isEditing = false;
  let saveError = '';

  function startEdit() {
    isEditing = true;
  }

  function cancelEdit() {
    isEditing = false;
  }

  function handlePhotoUpload(e: CustomEvent<File[]>) {
    dispatch('photoUpload', e.detail);
  }

  function handleAdd() {
    isEditing = true;
    saveError = '';
    dispatch('add', { 
      id: crypto.randomUUID(), 
      record: { 
        date: new Date().toISOString().split('T')[0],
        photos: []
      } 
    });
  }
  
  async function handleSave(event: CustomEvent<{ id: string; record: Partial<GrowthRecord> }>) {
    try {
      if (!record) {
        await dispatch('add', event.detail);
      } else {
        await dispatch('edit', event.detail);
      }
    } catch (error) {
      saveError = error instanceof Error ? error.message : 'Unknown error';
    }
  }
</script>

<div class="growth-record" transition:fade>
  {#if isEditing}
    <GrowthRecordForm 
      {record}
      saveError={saveError}
      on:save={handleSave}
      on:error={(e) => {
        saveError = e.detail;
      }}
      on:cancel={() => {
        cancelEdit();
        saveError = '';
      }}
      on:photoUpload={handlePhotoUpload}
    />
  {:else}
    {#if record}
      <div class="record-display">
        <h3>{record.date}</h3>
        {#if record.weight}
          <p>体重: {record.weight}kg</p>
        {/if}
        {#if record.height}
          <p>身高: {record.height}cm</p>
        {/if}
        {#if record.notes}
          <p>备注: {record.notes}</p>
        {/if}
        
        {#if editable}
          <div class="actions">
            <button on:click={startEdit}>编辑</button>
            <button on:click={() => dispatch('delete', { id: record.id })}>删除</button>
          </div>
        {/if}
      </div>
    {:else}
      {#if editable}
        <button on:click={handleAdd}>添加记录</button>
      {/if}
    {/if}
  {/if}
</div>

<style>
  .growth-record {
    margin: 1rem 0;
    padding: 1rem;
    border: 1px solid #eee;
    border-radius: 4px;
  }

  .record-display {
    display: grid;
    gap: 0.5rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }
</style>
