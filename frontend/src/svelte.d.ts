declare module '*.svelte' {
  import { SvelteComponent } from 'svelte'
  const component: SvelteComponent
  export default component
}
