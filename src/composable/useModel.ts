import { ref, watch } from 'vue'

export interface PetConfig {
  id: string
  name: string
  url: string
  preview?: string
  loopAction: string
  availableClickActions: string[]
}

export const petList: PetConfig[] = [
  {
    id: 'logo',
    name: '绘',
    url: 'logo.glb',
    preview: 'logo.png', // 使用文字表情
    loopAction: 'Idle',
    availableClickActions: ['Jump', 'Blink', 'Greet'],
  },
  {
    id: 'dog',
    name: '小狗',
    url: 'dog.glb',
    preview: '🐶', // 使用图片路径
    loopAction: 'Idle',
    availableClickActions: ['Jump', 'Blink'],
  },
  {
    id: 'cat',
    name: '小猫',
    url: 'cat.glb',
    preview: '🐱', // 使用图片路径
    loopAction: 'Idle',
    availableClickActions: ['Jump', 'Blink'],
  },
]

// 从本地存储获取初始宠物 ID
const savedPetId = localStorage.getItem('selectedPetId') || 'logo'
const currentPetId = ref(savedPetId)

// 监听跨窗口同步 (Electron 不同窗口是不同进程)
window.addEventListener('storage', (e) => {
  if (e.key === 'selectedPetId' && e.newValue) {
    console.log('[useModel] Storage event detected pet change:', e.newValue)
    currentPetId.value = e.newValue
  }
})

// 当前选中的宠物配置
const currentPet = ref<PetConfig>(
  petList.find((p) => p.id === currentPetId.value) || petList[0]
)

// 模型url
const url = ref(currentPet.value.url)

// 循环动画
const loopAction = ref({
  action: currentPet.value.loopAction,
  isLoop: true,
})

// 是否点击动画
const clickAction = ref({
  action: currentPet.value.availableClickActions[0] || 'Jump',
  isEnable: true,
})

// 可用的点击交互动作列表
const availableClickActions = ref(currentPet.value.availableClickActions)

// 运动通知
const clickActionPlay = ref(0)

// 监听宠物 ID 变化并更新配置
watch(currentPetId, (newId) => {
  const pet = petList.find((p) => p.id === newId) || petList[0]
  currentPet.value = pet
  url.value = pet.url
  loopAction.value.action = pet.loopAction
  availableClickActions.value = pet.availableClickActions
  clickAction.value.action = pet.availableClickActions[0] || 'Jump'
  localStorage.setItem('selectedPetId', newId)
})

export const useModel = () => {
  const clickActionPlayMessage = () => {
    clickActionPlay.value += 1
  }

  const switchPet = (id: string) => {
    currentPetId.value = id
  }

  return {
    url,
    loopAction,
    clickAction,
    availableClickActions,
    clickActionPlay,
    clickActionPlayMessage,
    currentPetId,
    petList,
    switchPet,
  }
}
