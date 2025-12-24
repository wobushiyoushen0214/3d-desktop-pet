

<template>
  <SubWindowLayout title="任务管理">
    <div class="h-full flex flex-col bg-gray-50">
      <!-- Tab 切换 -->
      <div class="px-6 pt-6 pb-2 bg-white border-b border-gray-100">
        <div class="flex p-1 bg-gray-100/80 rounded-xl">
          <button
            class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ease-out"
            :class="[
              activeTab === 'list'
                ? 'bg-white text-green-600 shadow-sm scale-[1.02]'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
            ]"
            @click="switchTab('list')"
          >
            任务列表
          </button>
          <button
            class="flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ease-out"
            :class="[
              activeTab === 'add'
                ? 'bg-white text-green-600 shadow-sm scale-[1.02]'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
            ]"
            @click="switchTab('add')"
          >
            添加任务
          </button>
        </div>
      </div>

      <!-- 任务列表 -->
      <div v-show="activeTab === 'list'" class="flex-1 overflow-y-auto p-6">
        <div v-if="tasks.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
          <span class="text-4xl mb-4">📝</span>
          <p>暂无任务</p>
        </div>
        <div v-else class="flex flex-col gap-4">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="group bg-white rounded-xl p-5 shadow-sm border border-gray-100 transition-all duration-300 hover:shadow-md hover:translate-y-[-2px]"
            :class="[
              task.status === 'completed' ? 'bg-gray-50/50' : '',
              getDueStatus(task) === 'overdue' ? 'border-red-200 bg-red-50/10' : '',
            ]"
          >
            <!-- 任务头部 -->
            <div class="flex justify-between items-start gap-5">
              <div class="flex items-center gap-3 flex-1">
                <!-- 优先级指示器 -->
                <div 
                  class="w-2.5 h-2.5 rounded-full shadow-sm flex-shrink-0"
                  :class="{
                    'bg-red-500 shadow-red-200': task.priority === 'high',
                    'bg-orange-500 shadow-orange-200': task.priority === 'medium',
                    'bg-green-500 shadow-green-200': task.priority === 'low'
                  }"
                  :title="'优先级: ' + (task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低')"
                ></div>

                <div class="flex flex-col gap-1 flex-1">
                  <div class="flex items-center gap-2">
                    <h4 
                      class="font-medium text-gray-800 text-lg transition-all"
                      :class="{ 'line-through text-gray-400': task.status === 'completed' }"
                    >
                      {{ task.title }}
                    </h4>
                    <div
                      v-if="task.dueDate"
                      class="text-[10px] px-2 py-0.5 rounded-full border"
                      :class="[
                        getDueStatus(task) === 'overdue'
                          ? 'bg-red-50 text-red-600 border-red-100'
                          : '',
                        getDueStatus(task) === 'upcoming'
                          ? 'bg-orange-50 text-orange-600 border-orange-100'
                          : '',
                        getDueStatus(task) === 'normal'
                          ? 'bg-gray-50 text-gray-500 border-gray-100'
                          : '',
                      ]"
                    >
                      {{ formatDate(task.dueDate) }} 截止
                    </div>
                  </div>
                </div>
              </div>

              <!-- 任务操作 -->
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <select
                  :value="task.status"
                  @change="updateTaskStatus(task, ($event.target as HTMLSelectElement)?.value as Task['status'])"
                  class="px-2.5 py-1.5 rounded-lg border border-gray-200 text-xs bg-white hover:border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
                  :class="{
                    'text-green-600 font-medium': task.status === 'completed',
                    'text-blue-600': task.status === 'in-progress',
                    'text-gray-600': task.status === 'pending'
                  }"
                >
                  <option value="pending">待处理</option>
                  <option value="in-progress">进行中</option>
                  <option value="completed">已完成</option>
                </select>
                
                <select
                  :value="task.priority"
                  @change="updateTaskPriority(task, ($event.target as HTMLSelectElement).value as Task['priority'])"
                  class="px-2.5 py-1.5 rounded-lg border border-gray-200 text-xs bg-white hover:border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
                >
                  <option value="low">低优先级</option>
                  <option value="medium">中优先级</option>
                  <option value="high">高优先级</option>
                </select>

                <button
                  @click="deleteTask(task.id!)"
                  class="p-1.5 bg-red-50 text-red-500 rounded-lg hover:bg-red-100 hover:text-red-600 transition-colors"
                  title="删除任务"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>

            <p 
              class="text-sm mt-3 mb-4 leading-relaxed pl-5 border-l-2 border-gray-50"
              :class="task.status === 'completed' ? 'text-gray-400' : 'text-gray-500'"
            >
              {{ task.description || '暂无描述' }}
            </p>

            <div class="flex items-center gap-2 text-[10px] text-gray-400 pl-5">
              <span>📅 创建于 {{ new Date(task.createdAt).toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加任务表单 -->
      <div v-show="activeTab === 'add'" class="flex-1 overflow-y-auto p-6">
        <div class="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <h3 class="text-xl font-semibold text-gray-800 mb-6">创建新任务</h3>
          <div class="space-y-6">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">任务标题 <span class="text-red-500">*</span></label>
              <input
                v-model="newTask.title"
                type="text"
                placeholder="例如：完成项目报告"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 hover:border-gray-300"
              />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">任务描述</label>
              <textarea
                v-model="newTask.description"
                rows="3"
                placeholder="添加一些备注信息..."
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 hover:border-gray-300 resize-none"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-6">
              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">优先级</label>
                <div class="relative">
                  <select
                    v-model="newTask.priority"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm appearance-none bg-white transition-all focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 hover:border-gray-300 cursor-pointer"
                  >
                    <option value="low">低优先级</option>
                    <option value="medium">中优先级</option>
                    <option value="high">高优先级</option>
                  </select>
                  <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-gray-700">截止时间</label>
                <input
                  v-model="newTask.dueDate"
                  type="datetime-local"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 hover:border-gray-300"
                />
              </div>
            </div>

            <div class="pt-4">
              <button
                @click="handleAddTask"
                :disabled="!isFormValid"
                class="w-full py-3.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-300 transform active:scale-[0.98]"
                :class="[
                  isFormValid
                    ? 'bg-green-600 text-white hover:bg-green-700 shadow-lg shadow-green-500/30'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed',
                ]"
              >
                添加任务
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <Toast
      message="任务标题已存在，请使用不同的标题"
      type="warning"
      v-model="showToast"
    />
  </SubWindowLayout>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import SubWindowLayout from '../components/SubWindowLayout.vue'
import type { Task } from '../db'
import db from '../db'
import Toast from '../components/Toast.vue'
// 任务列表数据
const tasks = ref<Task[]>([])
// 当前激活的 tab
const activeTab = ref<'list' | 'add'>('list')
// 新任务表单数据
const newTask = ref({
  title: '',
  description: '',
  priority: 'medium' as const,
  dueDate: '',
})

// 初始化加载数据
onMounted(async () => {
  await loadTasks()
})

/**
 * 获取任务的截止状态
 * @param task 任务对象
 * @returns 'overdue' | 'upcoming' | 'normal'
 */
function getDueStatus(task: Task) {
  if (!task.dueDate) return 'normal'
  const now = Date.now()
  const dueDate = new Date(task.dueDate).getTime()

  // 已逾期
  if (dueDate < now && task.status !== 'completed') {
    return 'overdue'
  }
  // 即将到期（24小时内）
  if (dueDate - now < 24 * 60 * 60 * 1000 && task.status !== 'completed') {
    return 'upcoming'
  }
  return 'normal'
}

/**
 * 格式化日期显示
 * @param timestamp 时间戳
 * @returns 格式化后的日期字符串
 */
function formatDate(timestamp: number) {
  const date = new Date(timestamp)
  const now = new Date()

  // 将两个日期都转换为当天 00:00:00 的时间戳来比较天数差异
  const dateDay = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const diffDays = Math.floor(
    (dateDay.getTime() - nowDay.getTime()) / (1000 * 60 * 60 * 24)
  )

  if (diffDays === 0) {
    return (
      '今天 ' +
      date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    )
  } else if (diffDays === 1) {
    return (
      '明天 ' +
      date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    )
  } else if (diffDays === -1) {
    return (
      '昨天 ' +
      date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    )
  } else if (diffDays > 1 && diffDays < 7) {
    return (
      `${diffDays}天后 ` +
      date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    )
  } else if (diffDays < -1 && diffDays > -7) {
    return (
      `${-diffDays}天前 ` +
      date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    )
  } else {
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }
}

/**
 * 加载所有任务
 */
async function loadTasks() {
  tasks.value = await db.tasks.toArray()
  // 按截止时间和创建时间排序
  tasks.value.sort((a, b) => {
    // 未完成的任务优先
    if (a.status !== b.status) {
      return a.status === 'completed' ? 1 : -1
    }
    // 有截止时间的任务优先
    if (!!a.dueDate !== !!b.dueDate) {
      return a.dueDate ? -1 : 1
    }
    // 按截止时间排序
    if (a.dueDate && b.dueDate) {
      return a.dueDate - b.dueDate
    }
    // 最后按创建时间排序
    return b.createdAt - a.createdAt
  })
}

/**
 * 检查表单是否有效
 */
const isFormValid = computed(() => {
  return newTask.value.title.trim() !== ''
})
const showToast = ref(false)
/**
 * 添加新任务
 */
async function addTask() {
  if (!newTask.value.title.trim()) {
    throw new Error()
  }
  // 检查标题是否重复
  const existingTask = tasks.value.find((t) => t.title === newTask.value.title)
  if (existingTask) {
    showToast.value = true
    throw new Error()
  }

  await db.addTask({
    title: newTask.value.title,
    description: newTask.value.description,
    status: 'pending',
    priority: newTask.value.priority,
    dueDate: newTask.value.dueDate
      ? new Date(newTask.value.dueDate).getTime()
      : undefined,
  })

  // 重置表单
  newTask.value = {
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
  }

  await loadTasks()
}

/**
 * 更新任务状态
 */
async function updateTaskStatus(task: Task, newStatus: Task['status']) {
  await db.updateTask(task.id!, { status: newStatus })
  await loadTasks()
}

/**
 * 更新任务优先级
 */
async function updateTaskPriority(task: Task, newPriority: Task['priority']) {
  await db.updateTask(task.id!, { priority: newPriority })
  await loadTasks()
}

/**
 * 删除任务
 */
async function deleteTask(taskId: string) {
  if (confirm('确定要删除这个任务吗？')) {
    await db.tasks.delete(taskId)
    await loadTasks()
  }
}

/**
 * 切换 tab
 */
function switchTab(tab: 'list' | 'add') {
  activeTab.value = tab
}

/**
 * 添加任务后切换到列表视图
 */
async function handleAddTask() {
  if (!isFormValid.value) return
  try {
    await addTask()
    switchTab('list')
  } catch (error) {}
}
</script>
<style scoped>
/* 只保留滚动条相关样式，其他都用 Tailwind 类替代 */
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
