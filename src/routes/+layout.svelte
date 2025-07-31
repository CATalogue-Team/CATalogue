<script lang="ts">
  import '../app.css';
</script>

<div class="app-container">
  <nav>
    <a href="/">首页</a>
    <a href="/cats">猫咪档案</a>
    <a href="/community">社区</a>
  </nav>

  <slot />
</div>

<style>
  .app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  nav {
    background: #333;
    padding: 1rem;
  }
  
  nav a {
    color: white;
    margin-right: 1rem;
    text-decoration: none;
  }
  
  nav a:hover {
    text-decoration: underline;
  }
</style>
