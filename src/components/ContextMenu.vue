<!--
 * @Author: LiZhiWei
 * @Date: 2025-12-23 14:53:55
 * @LastEditors: LiZhiWei
 * @LastEditTime: 2025-12-24 09:26:31
 * @Description: 
-->


<template>
  <div class="fixed z-[1000] right-4 top-12 flex flex-col gap-3">
    <div
      v-for="item in menuItems"
      :key="item.id"
      class="group relative flex items-center justify-center"
      @click="handleMenuClick(item.id)"
    >
      <!-- 图标按钮 -->
      <div
        class="w-5 h-5 rounded-full bg-white/60 backdrop-blur-md shadow-lg flex items-center justify-center cursor-pointer transition-all duration-300 hover:bg-white hover:scale-110 hover:shadow-xl text-lg border border-white/40"
      >
        <span>{{ item.icon }}</span>
      </div>

      <!-- Tooltip 提示 -->
      <div
        class="absolute right-12 px-3 py-1.5 bg-gray-800/80 backdrop-blur-sm text-white text-xs rounded-md opacity-0 translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300 whitespace-nowrap pointer-events-none"
      >
        {{ item.label }}
        <!-- 小三角 -->
        <div
          class="absolute right-[-4px] top-1/2 -translate-y-1/2 w-0 h-0 border-y-[4px] border-y-transparent border-l-[4px] border-l-gray-800/80"
        ></div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { useModel } from '../composable/useModel'
import { useUser } from '../composable/useUser'

const { loopAction } = useModel()
const { isLoggedIn } = useUser()

const emit = defineEmits(['close'])

const menuItems = computed(() => [
  { 
    id: 'login', 
    label: isLoggedIn.value ? '已登录账号' : '登录账号', 
    icon: isLoggedIn.value ? '✅' : '👤' 
  },
  { id: 'task', label: '添加任务', icon: '🔖' },
  { id: 'reminder', label: '添加提醒', icon: '⏰' },
  {
    id: 'pet',
    label: '宠物管理',
    icon: '🐶',
  },
  { id: 'exit', label: '退出应用', icon: '👋' },
])

const handleMenuClick = (menuId) => {
  const ipcRenderer = window.ipcRenderer

  switch (menuId) {
    case 'login':
      ipcRenderer.send('open-login-window')
      break
    case 'task':
      ipcRenderer.send('open-sub-window', {
        windowId: 'task',
        title: '任务管理',
      })
      break
    case 'reminder':
      ipcRenderer.send('open-sub-window', {
        windowId: 'reminder',
        title: '提醒管理',
      })
      break
    case 'pet':
      // ipcRenderer.send('open-sub-window', {
      //   windowId: 'pet',
      //   title: '宠物管理',
      // })
      if (loopAction.value.isLoop) {
        loopAction.value.isLoop = false
      } else {
        loopAction.value.isLoop = true
      }
      break
    case 'exit':
      // ipcRenderer.send('exit-app')
      ipcRenderer.send('minimize-main-window')
      break
  }
  emit('close')
}
</script>