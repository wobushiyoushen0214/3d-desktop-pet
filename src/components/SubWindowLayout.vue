

<template>
  <div class="sub-window-layout">
    <header class="window-header">
      <h1>{{ title }}</h1>
    </header>
    <main class="content scrollbar-thin">
      <slot></slot>
    </main>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>
<style scoped>
.sub-window-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica,
    Arial, sans-serif;
}

.window-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  -webkit-app-region: drag;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.window-header h1 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  letter-spacing: 0.5px;
  -webkit-app-region: no-drag;
}

.content {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  position: relative;
}

/* 自定义滚动条 */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.8);
}
</style>
