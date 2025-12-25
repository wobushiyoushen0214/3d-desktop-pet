<template>
  <SubWindowLayout title="绘 AI">
    <div class="h-full flex flex-col bg-white">
      <!-- Chat List -->
      <div class="flex-1 overflow-y-auto px-4 py-6 space-y-6" ref="scrollRef">
        <!-- Empty State with Prompts -->
        <template v-if="messages.length === 0">
          <div class="h-full flex flex-col items-center justify-center space-y-8 px-8 pb-20">
            <div class="text-center space-y-4">
              <div class="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                <RobotOutlined class="text-3xl text-blue-500" />
              </div>
              <h3 class="text-lg font-medium text-gray-800">我是你的 AI 助手</h3>
              <p class="text-gray-500 text-sm">我可以帮你回答问题、编写代码或提供建议。</p>
            </div>
            
            <!-- Quick Prompts -->
            <div class="w-full grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button 
                v-for="prompt in defaultPrompts" 
                :key="prompt"
                class="text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-xl text-sm text-gray-700 transition-colors duration-200 border border-transparent hover:border-blue-100 hover:text-blue-600 hover:shadow-sm"
                @click="usePrompt(prompt)"
              >
                {{ prompt }}
              </button>
            </div>
          </div>
        </template>
        
        <!-- Message List -->
        <div v-for="(msg, index) in messages" :key="index">
          <Bubble
            :content="msg.content"
            :placement="msg.role === 'user' ? 'end' : 'start'"
            :styles="{ content: { padding: 0, backgroundColor: 'transparent', boxShadow: 'none' } }"
          >
            <template #avatar>
              <a-avatar 
                :size="32" 
                class="flex-shrink-0"
                :class="msg.role === 'user' ? 'bg-blue-500' : 'bg-orange-400'"
              >
                <template #icon>
                  <UserOutlined v-if="msg.role === 'user'" />
                  <RobotOutlined v-else />
                </template>
              </a-avatar>
            </template>
            
            <template #message>
              <div 
                class="px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm min-w-[40px]"
                :class="[
                  msg.role === 'user' 
                    ? 'bg-blue-500 text-white rounded-tr-sm' 
                    : 'bg-gray-100 text-gray-800 rounded-tl-sm'
                ]"
              >
                <div 
                  v-if="msg.role === 'assistant'" 
                  class="markdown-body" 
                  :class="{ 'typing-cursor': streaming && index === messages.length - 1 }"
                  v-html="renderMarkdown(msg.content)"
                ></div>
                <div v-else class="whitespace-pre-wrap">{{ msg.content }}</div>
                
                <div v-if="msg.error" class="text-xs text-red-100 mt-2 border-t border-red-400/30 pt-1 flex items-center">
                  <WarningOutlined class="mr-1" /> {{ msg.error }}
                </div>
              </div>
            </template>
          </Bubble>
        </div>

        <!-- Loading Indicator (when waiting for first token) -->
        <div v-if="loading && !streaming" class="flex gap-3 pl-1">
           <a-avatar :size="32" class="bg-orange-400 flex-shrink-0">
             <template #icon><RobotOutlined /></template>
           </a-avatar>
           <div class="bg-gray-100 px-4 py-3 rounded-2xl rounded-tl-sm">
             <div class="flex space-x-1 h-5 items-center">
               <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
               <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
               <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
             </div>
           </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-4 bg-white border-t border-gray-100 shadow-[0_-4px_20px_rgba(0,0,0,0.02)] z-10">
        <Sender
          v-model:value="inputValue"
          placeholder="输入消息..."
          :loading="loading && !streaming"
          class="custom-sender"
          @submit="sendMessage"
        />
      </div>
    </div>
  </SubWindowLayout>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import SubWindowLayout from '../components/SubWindowLayout.vue'
import { UserOutlined, RobotOutlined, WarningOutlined } from '@ant-design/icons-vue'
import { Bubble, Sender } from 'ant-design-x-vue'
import MarkdownIt from 'markdown-it'

// Markdown setup
const md = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: true
})

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  error?: string
}

const messages = ref<Message[]>([])
const inputValue = ref('')
const loading = ref(false)
const streaming = ref(false)
const scrollRef = ref<HTMLElement | null>()

const defaultPrompts = [
  '你好，请介绍一下你自己',
  '给我讲一个有趣的笑话',
  '如何学习 Vue 3？',
  '写一段 Python 冒泡排序代码'
]

// Scroll to bottom
let scrollTask: number | null = null

const scrollToBottom = (behavior: ScrollBehavior = 'auto') => {
  if (scrollTask) return
  
  scrollTask = requestAnimationFrame(async () => {
    await nextTick()
    if (scrollRef.value) {
      scrollRef.value.scrollTo({
        top: scrollRef.value.scrollHeight,
        behavior
      })
    }
    scrollTask = null
  })
}

const renderMarkdown = (text: string) => {
  return md.render(text || '')
}

const usePrompt = (text: string) => {
  inputValue.value = text
  sendMessage()
}

const sendMessage = () => {
  const content = inputValue.value.trim()
  if (!content || (loading.value && !streaming.value)) return

  // Add user message
  messages.value.push({ role: 'user', content })
  inputValue.value = ''
  loading.value = true
  streaming.value = false
  scrollToBottom('smooth')

  // Prepare context
  const history = messages.value.map(m => ({ role: m.role, content: m.content }))

  // Send to IPC
  window.ipcRenderer.send('chat-send', {
    messages: history,
    model: 'llama3'
  })
}

// IPC Listeners
let buffer = ''

onMounted(() => {
  const ipc = window.ipcRenderer

  ipc.on('chat-reply-chunk', (_event, chunk: string) => {
    buffer += chunk
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (!line.trim()) continue
      try {
        const data = JSON.parse(line)
        if (data.message && data.message.content) {
          if (!streaming.value) {
            streaming.value = true
            messages.value.push({ role: 'assistant', content: '' })
            scrollToBottom('smooth')
          }
          const aiMsg = messages.value[messages.value.length - 1]
          if (aiMsg && aiMsg.role === 'assistant') {
             // Check if user is near bottom before update
             const div = scrollRef.value
             const isNearBottom = div ? (div.scrollHeight - div.scrollTop - div.clientHeight < 100) : true
             
             aiMsg.content += data.message.content
             
             if (isNearBottom) {
               scrollToBottom('auto')
             }
          }
        }
        if (data.done) {
          loading.value = false
          streaming.value = false
        }
      } catch (e) {
        console.error('JSON parse error', e)
      }
    }
  })

  ipc.on('chat-reply-done', () => {
    loading.value = false
    streaming.value = false
    buffer = ''
  })

  ipc.on('chat-reply-error', (_event, error: string) => {
    loading.value = false
    streaming.value = false
    const aiMsg = messages.value[messages.value.length - 1]
    if (aiMsg) {
      aiMsg.error = 'Error: ' + error
    }
  })
})

onUnmounted(() => {
  window.ipcRenderer.removeAllListeners('chat-reply-chunk')
  window.ipcRenderer.removeAllListeners('chat-reply-done')
  window.ipcRenderer.removeAllListeners('chat-reply-error')
})
</script>

<style scoped>
/* Markdown Styles */
:deep(.markdown-body) {
  font-size: 14px;
  line-height: 1.6;
}
:deep(.markdown-body p) {
  margin-bottom: 0.5em;
}
:deep(.markdown-body p:last-child) {
  margin-bottom: 0;
}
:deep(.markdown-body pre) {
  background: #2d2d2d;
  color: #ccc;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}
:deep(.markdown-body code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.9em;
}
:deep(.markdown-body pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}
:deep(.markdown-body ul), :deep(.markdown-body ol) {
  padding-left: 1.5em;
  margin-bottom: 0.5em;
}
:deep(.markdown-body li) {
  margin-bottom: 0.2em;
}

/* Typing Cursor Effect */
.typing-cursor > :last-child::after {
  content: '';
  display: inline-block;
  vertical-align: text-bottom;
  width: 8px;
  height: 16px;
  background-color: currentColor;
  margin-left: 4px;
  border-radius: 1px;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}
</style>
