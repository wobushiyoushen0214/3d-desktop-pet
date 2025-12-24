
<template>
  <SubWindowLayout title="提醒管理">
    <div class="h-full flex flex-col bg-gray-50">
      <!-- Tab 切换 -->
      <div class="px-6 pt-6 pb-2 bg-white border-b border-gray-100">
        <div class="flex p-1 bg-gray-100/80 rounded-xl">
          <button
            class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ease-out"
            :class="[
              activeTab === 'list'
                ? 'bg-white text-blue-600 shadow-sm scale-[1.02]'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
            ]"
            @click="switchTab('list')"
          >
            提醒列表
          </button>
          <button
            class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ease-out"
            :class="[
              activeTab === 'add'
                ? 'bg-white text-blue-600 shadow-sm scale-[1.02]'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
            ]"
            @click="switchTab('add')"
          >
            添加提醒
          </button>
        </div>
      </div>

      <!-- 提醒列表 -->
      <div v-show="activeTab === 'list'" class="flex-1 overflow-y-auto p-6">
        <div v-if="reminders.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
          <span class="text-4xl mb-4">📭</span>
          <p>暂无提醒事项</p>
        </div>
        <div v-else class="flex flex-col gap-4">
          <div
            v-for="reminder in reminders"
            :key="reminder.id"
            class="group bg-white rounded-xl p-5 shadow-sm border border-gray-100 transition-all duration-300 hover:shadow-md hover:translate-y-[-2px]"
          >
            <div class="flex justify-between items-start gap-5">
              <div class="flex items-center gap-3 flex-1">
                <!-- 状态指示点 -->
                <div 
                  class="w-2.5 h-2.5 rounded-full shadow-sm"
                  :class="reminder.isEnabled ? 'bg-green-500 shadow-green-200' : 'bg-gray-300'"
                ></div>
                
                <h4 class="font-medium text-gray-800 text-lg">{{ reminder.title }}</h4>
                <div
                  class="text-xs px-2.5 py-1 rounded-full bg-gray-50 text-gray-600 border border-gray-100 font-medium"
                >
                  {{ repeatTypeMap[reminder.repeatType] }}
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <button
                  v-if="reminder.repeatType !== 'none'"
                  @click="toggleReminderStatus(reminder)"
                  class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                  :class="
                    reminder.isEnabled
                      ? 'bg-orange-50 text-orange-600 hover:bg-orange-100'
                      : 'bg-green-50 text-green-600 hover:bg-green-100'
                  "
                >
                  {{ reminder.isEnabled ? '暂停' : '启用' }}
                </button>
                <button
                  @click="deleteReminder(reminder.id!)"
                  class="px-3 py-1.5 bg-red-50 text-red-600 rounded-lg text-xs font-medium hover:bg-red-100 transition-colors"
                >
                  删除
                </button>
              </div>
            </div>

            <p class="text-gray-500 text-sm mt-3 mb-4 leading-relaxed pl-5 border-l-2 border-gray-50">
              {{ reminder.description || '暂无描述' }}
            </p>

            <div class="flex items-center gap-4 text-xs text-gray-400 pl-5">
              <div v-if="reminder.repeatType === 'custom'" class="flex items-center gap-1">
                <span>⏱️</span>
                <span>间隔 {{ reminder.customInterval }} 分钟</span>
              </div>
              <div v-if="reminder.repeatType === 'daily'" class="flex items-center gap-1">
                <span>📅</span>
                <span>每天 {{ reminder.dailyTime }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span>🔔</span>
                <span>下次: </span>
                <span
                  class="text-blue-500 font-medium cursor-help"
                  :title="newReminderTime"
                  @mouseenter="getLatestReminderTime(reminder.id!)"
                >
                  {{ newReminderTime || '计算中...' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加提醒表单 -->
      <div v-show="activeTab === 'add'" class="flex-1 overflow-y-auto p-6">
        <div class="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <h3 class="text-xl font-semibold text-gray-800 mb-6">创建新提醒</h3>
          <div class="space-y-6">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">提醒标题 <span class="text-red-500">*</span></label>
              <input
                v-model="newReminder.title"
                type="text"
                placeholder="例如：喝水、休息一下"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 hover:border-gray-300"
              />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">提醒描述</label>
              <textarea
                v-model="newReminder.description"
                rows="3"
                placeholder="添加一些备注信息..."
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 hover:border-gray-300 resize-none"
              >
              </textarea>
            </div>

            <div class="grid grid-cols-2 gap-6">
              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">重复类型</label>
                <div class="relative">
                  <select
                    v-model="newReminder.repeatType"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm appearance-none bg-white transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 hover:border-gray-300 cursor-pointer"
                  >
                    <option value="none">不重复</option>
                    <option value="custom">自定义间隔</option>
                    <option value="daily">每天</option>
                  </select>
                  <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">
                  {{ newReminder.repeatType === 'none' ? '提醒时间' : '首次提醒时间' }} <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="newReminder.reminderTime"
                  type="datetime-local"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 hover:border-gray-300"
                />
              </div>
            </div>

            <div v-if="newReminder.repeatType === 'custom'" class="flex flex-col gap-2 bg-blue-50 p-4 rounded-xl border border-blue-100">
              <label class="text-sm font-medium text-blue-800">间隔时间（分钟）</label>
              <div class="flex items-center gap-3">
                <input
                  v-model="newReminder.customInterval"
                  type="number"
                  min="1"
                  class="flex-1 px-4 py-3 border border-blue-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
                <span class="text-sm text-blue-600 font-medium">分钟后再次提醒</span>
              </div>
            </div>

            <div v-if="newReminder.repeatType === 'daily'" class="flex flex-col gap-2 bg-blue-50 p-4 rounded-xl border border-blue-100">
              <label class="text-sm font-medium text-blue-800">每天提醒时间</label>
              <input
                v-model="newReminder.dailyTime"
                type="time"
                class="w-full px-4 py-3 border border-blue-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>

            <div class="pt-4">
              <button
                @click="handleAddReminder"
                :disabled="!isFormValid"
                class="w-full py-3.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-300 transform active:scale-[0.98]"
                :class="[
                  isFormValid
                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-500/30'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed',
                ]"
              >
                添加提醒
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <Toast
      message="提醒标题已存在，请使用不同的标题"
      type="warning"
      v-model="showToast"
    />
  </SubWindowLayout>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import SubWindowLayout from '../components/SubWindowLayout.vue'
import type { Reminder } from '../db'
import { RepeatType } from '../db'
import db from '../db'
import Toast from '../components/Toast.vue'
// 提醒列表数据
const reminders = ref<Reminder[]>([])
// 当前激活的 tab
const activeTab = ref<'list' | 'add'>('list')
// 新提醒表单数据
const newReminder = ref({
  title: '',
  description: '',
  isEnabled: true,
  repeatType: 'none' as RepeatType,
  reminderTime: '',
  customInterval: 30,
  dailyTime: '',
})
const showToast = ref(false)
// 重复类型显示文本
const repeatTypeMap = {
  none: '不重复',
  custom: '自定义间隔',
  daily: '每天',
}

onMounted(async () => {
  await loadReminders()
})

/**
 * 格式化时间显示
 */
function formatDateTime(timestamp: number) {
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 加载所有提醒
 */
async function loadReminders() {
  reminders.value = await db.reminders.toArray()
  // 按提醒时间和创建时间排序
  reminders.value.sort((a, b) => {
    if (a.reminderTime && b.reminderTime) {
      return (
        new Date(a.reminderTime).getTime() - new Date(b.reminderTime).getTime()
      )
    }
    return b.createdAt - a.createdAt
  })
}

/**
 * 检查提醒表单是否有效
 */
const isFormValid = computed(() => {
  const form = newReminder.value
  const basicFieldsValid = form.title.trim() !== '' && form.reminderTime !== ''

  if (form.repeatType === 'custom') {
    return basicFieldsValid && form.customInterval > 0
  }

  if (form.repeatType === 'daily') {
    return basicFieldsValid && form.dailyTime !== ''
  }

  return basicFieldsValid
})

/**
 * 添加新提醒
 */
async function addReminder() {
  if (!newReminder.value.title.trim() || !newReminder.value.reminderTime) {
    throw new Error()
  }
  // 检查标题是否重复
  const existingReminder = reminders.value.find(
    (r) => r.title === newReminder.value.title
  )
  if (existingReminder) {
    showToast.value = true
    throw new Error()
  }

  const reminderTime = new Date(newReminder.value.reminderTime).getTime()

  await db.addReminder({
    title: newReminder.value.title,
    description: newReminder.value.description,
    isEnabled: newReminder.value.isEnabled,
    repeatType: newReminder.value.repeatType,
    reminderTime: new Date(reminderTime).toISOString(),
    customInterval:
      newReminder.value.repeatType === 'custom'
        ? newReminder.value.customInterval
        : undefined,
    dailyTime:
      newReminder.value.repeatType === 'daily'
        ? newReminder.value.dailyTime
        : undefined,
  })

  // 重置表单
  newReminder.value = {
    title: '',
    description: '',
    isEnabled: true,
    repeatType: 'none' as RepeatType,
    reminderTime: '',
    customInterval: 30,
    dailyTime: '',
  }

  await loadReminders()
}

/**
 * 切换提醒启用状态
 */
async function toggleReminderStatus(reminder: Reminder) {
  await db.toggleReminder(reminder.id!, !reminder.isEnabled)
  await loadReminders()
}

/**
 * 删除提醒
 */
async function deleteReminder(reminderId: string) {
  if (confirm('确定要删除这个提醒吗？')) {
    await db.reminders.delete(reminderId)
    await loadReminders()
  }
}

/**
 * 切换 tab
 */
function switchTab(tab: 'list' | 'add') {
  activeTab.value = tab
}

/**
 * 添加提醒后切换到列表视图
 */
async function handleAddReminder() {
  if (!isFormValid.value) return
  try {
    await addReminder()
    switchTab('list')
  } catch (error) {}
}
const newReminderTime = ref('')
/**
 * 获取最新的提醒时间
 */
async function getLatestReminderTime(reminderId: string) {
  const reminder = await db.reminders.get(reminderId)
  newReminderTime.value = reminder?.reminderTime
    ? formatDateTime(new Date(reminder.reminderTime).getTime())
    : '无'
}
</script>

<style scoped>
.tab-content::-webkit-scrollbar {
  @apply w-2;
}

.tab-content::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.tab-content::-webkit-scrollbar-thumb {
  @apply bg-gray-400 rounded hover:bg-gray-500;
}
</style>
