
<template>
  <!-- 主窗口显示宠物模型和右键菜单 -->
  <div class="main-container" @contextmenu.prevent="handleContextMenu">
    <!-- 3D 背景层：直接作为容器子元素，不加额外的 wrapper，避免 pointer-events 干扰 -->
    <TresCanvas v-bind="gl" >
      <TresPerspectiveCamera :position="[0, 0, 4]" />
      <OrbitControls :enable-zoom="false" :enable-pan="false" />
      <Suspense>
        <!-- 移除 click.stop，防止阻止 DOM 事件冒泡 -->
        <TresGroup @click="handleClick">
          <Pet :key="url" />
        </TresGroup>
      </Suspense>
      <TresDirectionalLight v-bind="light" />
      <TresDirectionalLight :position="[-3, 2, 2]" :intensity="1.6" color="#ffffff" />
      <TresHemisphereLight :intensity="1.2" :ground-color="'#e5e7eb'" color="#ffffff" />
      <TresAmbientLight :intensity="2.8" />
    </TresCanvas>

    <!-- 当菜单显示时，覆盖一层透明遮罩，用于点击关闭菜单 -->
    <div v-show="showContextMenu" class="menu-overlay" @click="closeContextMenu"></div>

    <!-- 拖拽区域按钮 -->
    <div v-show="showContextMenu" class="drag-button">
      <ButtonIcon />
    </div>

    <!-- 右键菜单组件 -->
    <div v-show="showContextMenu" class="menu-wrapper">
      <ContextMenu @close="closeContextMenu" />
    </div>
  </div>
</template>
<script setup>
import { OrbitControls } from '@tresjs/cientos'
import { TresCanvas } from '@tresjs/core'
import { BasicShadowMap, NoToneMapping, SRGBColorSpace } from 'three'
import { onMounted, onUnmounted, ref } from 'vue'
import ButtonIcon from '../components/ButtonIcon.vue'
import ContextMenu from '../components/ContextMenu.vue'
import Pet from '../components/Pet3D.vue'
import { useModel } from '../composable/useModel'
import { useReminder } from '../composable/useReminder'

const { checkReminders } = useReminder()
const { clickActionPlayMessage, url } = useModel()

const showContextMenu = ref(false)
const handleContextMenu = (event) => {
  showContextMenu.value = !showContextMenu.value
}

// 点击其他地方关闭菜单
const closeContextMenu = () => {
  showContextMenu.value = false
}

const gl = {
  shadows: false,
  alpha: true,
  premultipliedAlpha: false,
  antialias: true,
  shadowMapType: BasicShadowMap,
  outputColorSpace: SRGBColorSpace,
  toneMapping: NoToneMapping,
  windowSize: true,
}

const petRef = ref(null)

const handleClick = (ev) => {
  // console.log('Model clicked!', ev)
  // 仅在菜单关闭时触发交互
  if (!showContextMenu.value) {
    clickActionPlayMessage()
  }
}

// 灯光设置 默认
const light = ref({
  color: '#fff',
  position: [0, 4, 3],
  intensity: 3.2,
})

// 定时器
let timer = null

onMounted(() => {
  // 立即检查一次
  checkReminders()
  // 设置定时检查
  timer = window.setInterval(checkReminders, 5000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.main-container {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: transparent;
  pointer-events: auto; /* 确保容器接收事件 */
}

.canvas-container {
  display: none; /* 已移除 */
}

.menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 998; /* 低于菜单，高于 Canvas */
  cursor: default;
}

.drag-button {
  position: absolute;
  top: 0px;
  right: 10px;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  -webkit-app-region: drag;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: grab;
  pointer-events: auto; /* 显式设置 */
}

.drag-button:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.05);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.drag-button:active {
  cursor: grabbing;
  transform: scale(0.95);
}

.menu-wrapper {
  position: fixed;
  inset: 0;
  z-index: 999;
  pointer-events: none;
}

.menu-wrapper > * {
  pointer-events: auto;
}
</style>
