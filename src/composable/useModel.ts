import { ref } from 'vue'

// 模型url
// const url = ref('rabbit.glb')
const url = ref('logo.glb')



// 循环动画
const loopAction = ref({
  action: 'Idle',
  isLoop: true,
})

// 是否点击动画
const clickAction = ref({
  action: 'Jump',
  isEnable: true,
})

// 可用的点击交互动作列表
const availableClickActions = ['Jump', 'Blink', 'Greet']

// 运动通知
const clickActionPlay = ref(0)

export const useModel = () => {
  const clickActionPlayMessage = () => {
    clickActionPlay.value += 1
  }

  return {
    url,
    loopAction,
    clickAction,
    availableClickActions,
    clickActionPlay,
    clickActionPlayMessage,
  }
}
