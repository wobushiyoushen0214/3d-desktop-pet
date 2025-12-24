<!--
 * @Author: LiZhiWei
 * @Date: 2025-12-23 14:53:55
 * @LastEditors: LiZhiWei
 * @LastEditTime: 2025-12-24 09:06:54
 * @Description: 
-->
<template>
  <div class="flex flex-col-reverse gap-4 p-4">
    <TransitionGroup name="reminder">
      <div
        v-for="reminder in reminderQueue"
        :key="reminder.id"
        class="relative bg-white/95 backdrop-blur-md rounded-2xl p-5 w-[220px] shadow-lg border border-white/50 animate-slide-in group hover:scale-[1.02] transition-all duration-300"
      >
        <!-- 气泡小三角 -->
        <div class="absolute -bottom-2 right-8 w-4 h-4 bg-white/95 transform rotate-45 border-b border-r border-white/50 shadow-sm"></div>

        <div class="flex justify-between items-start mb-3">
          <h3 class="font-bold text-gray-800 select-none truncate pr-2">{{ reminder.title }}</h3>
          <span
            class="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium border border-blue-100 whitespace-nowrap"
          >
            {{
              new Date(reminder.reminderTime).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })
            }}
          </span>
        </div>

        <p class="text-gray-600 text-xs mb-4 select-none leading-relaxed line-clamp-3 min-h-[1.5em]">
          {{ reminder.description || '主人，时间到啦！' }}
        </p>

        <button
          @click="acknowledgeReminder(reminder)"
          class="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-2 rounded-xl text-xs font-medium shadow-blue-200 hover:shadow-blue-300 hover:shadow-lg transition-all active:scale-95"
        >
          知道了
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useReminder } from '../composable/useReminder'

const { reminderQueue, acknowledgeReminder, checkReminders } = useReminder()
onMounted(async () => {
  // 监听主进程的更新消息
  window.ipcRenderer.on('update-reminders', async () => {
    await checkReminders()
  })
})
onUnmounted(() => {
  window.ipcRenderer.removeAllListeners('update-reminders')
})
</script>
<style scoped>
.reminder-enter-active,
.reminder-leave-active {
  transition: all 0.3s ease;
}

.reminder-enter-from,
.reminder-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}
</style>
