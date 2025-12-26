<!--
 * @Author: LiZhiWei
 * @Date: 2025-12-23 14:53:55
 * @LastEditors: LiZhiWei
 * @LastEditTime: 2025-12-26 10:19:18
 * @Description: 
-->

<template>
  <primitive :object="model" />
</template>
<script setup lang="ts">
import { useAnimations, useGLTF } from '@tresjs/cientos'
import * as THREE from 'three'
import { ref, watch } from 'vue'
import { useModel } from '../composable/useModel'

const { url, loopAction, clickAction, clickActionPlay, availableClickActions } = useModel()

watch(clickActionPlay, () => {
  hello()
})

watch(
  loopAction,
  () => {
    if (loopAction.value.isLoop) {
      if (currentLoopAction.value) {
        currentLoopAction.value.reset()
        currentLoopAction.value.play()
        isPlaying.value = true
      }
    } else {
      if (currentLoopAction.value) {
        currentLoopAction.value.stop()
        isPlaying.value = false
      }
    }
  },
  { deep: true }
)

const isPlaying = ref(false)

const modelUrl = ref('')

// 使用动态导入，但需要指定 glob 导入模式
const modules = import.meta.glob('/public/*.glb', {
  eager: true,
  import: 'default',
})

// 根据 url 获取对应的模型路径
const path = `/public/${url.value}`
const fallbackPath = '/public/logo_model_v14.glb'
modelUrl.value =
  (modules[path] as string) ||
  (modules[fallbackPath] as string) ||
  url.value ||
  'logo_model_v14.glb'

if (!modelUrl.value) {
  console.error(`Model not found: ${path}`)
} else {
  console.log(`Loading model from: ${modelUrl.value}`)
}

const { scene: model, animations } = await useGLTF(modelUrl.value)

const { actions } = useAnimations(animations, model)

console.log('Model animations:', animations.map((a) => a.name))
console.log('Animation actions:', Object.keys(actions))

// 点击动作
const currentClickAction = ref<any>(null)

// 点击动作
currentClickAction.value = Object.keys(actions).includes(
  clickAction.value.action
)
  ? actions[clickAction.value.action]
  : null

// 持续播放动作
const currentLoopAction = ref<any>(null)

currentLoopAction.value = Object.keys(actions).includes(loopAction.value.action)
  ? actions[loopAction.value.action]
  : null

if (loopAction.value.isLoop && currentLoopAction.value) {
  currentLoopAction.value.reset()
  currentLoopAction.value.play()
  isPlaying.value = true
}

let activeOneShot: any = null
let activeOneShotFinished: (() => void) | null = null

const isOneShotRunning = ref(false)

const traverseMeshes = (root: THREE.Object3D) => {
  const meshes: THREE.Mesh[] = []
  root.traverse((obj) => {
    if ((obj as THREE.Mesh).isMesh) meshes.push(obj as THREE.Mesh)
  })
  return meshes
}

const getEyeTargets = () => {
  const meshes = traverseMeshes(model)
  const byName = meshes.filter((m) => /eye|眼/i.test(m.name))
  if (byName.length) return byName
  const byMaterialName = meshes.filter((m) => {
    const material = m.material as any
    const materialName = material?.name
    return typeof materialName === 'string' && /eye|眼/i.test(materialName)
  })
  return byMaterialName
}

const tween = (durationMs: number, onUpdate: (t: number) => void) => {
  return new Promise<void>((resolve) => {
    const start = performance.now()
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs)
      onUpdate(t)
      if (t < 1) {
        requestAnimationFrame(tick)
      } else {
        resolve()
      }
    }
    requestAnimationFrame(tick)
  })
}

const easeInOutQuad = (t: number) =>
  t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2

const playBlink = async () => {
  const targets = getEyeTargets()
  if (!targets.length) return

  const baseScales = targets.map((m) => m.scale.clone())
  const minY = 0.08

  await tween(80, (t) => {
    const k = 1 - (1 - minY) * easeInOutQuad(t)
    targets.forEach((m, idx) => {
      const base = baseScales[idx]
      m.scale.set(base.x, base.y * k, base.z)
    })
  })

  await tween(140, (t) => {
    const k = minY + (1 - minY) * easeInOutQuad(t)
    targets.forEach((m, idx) => {
      const base = baseScales[idx]
      m.scale.set(base.x, base.y * k, base.z)
    })
  })
}

const playJump = async () => {
  const baseY = model.position.y
  const height = 0.32
  await tween(240, (t) => {
    model.position.y = baseY + height * easeInOutQuad(t)
  })
  await tween(260, (t) => {
    model.position.y = baseY + height * (1 - easeInOutQuad(t))
  })
  model.position.y = baseY
}

const playGltfOneShot = (action: any) => {
  return new Promise<void>((resolve) => {
    if (!action) return resolve()

    if (activeOneShot && activeOneShotFinished) {
      try {
        activeOneShot
          .getMixer()
          .removeEventListener('finished', activeOneShotFinished)
      } catch (e) {
      }
    }

    action.stop()
    action.reset()
    action.play()
    action.setLoop(THREE.LoopOnce, 1)
    action.clampWhenFinished = true

    const onFinished = () => {
      action.stop()
      action.getMixer().removeEventListener('finished', onFinished)
      resolve()
    }

    activeOneShot = action
    activeOneShotFinished = onFinished
    action.getMixer().addEventListener('finished', onFinished)
  })
}

const customActions: Record<string, () => Promise<void>> = {
  Blink: playBlink,
  Jump: playJump,
}

// 点击动作
const hello = () => {
  // console.log('Hello action triggered')
  if (!clickAction.value.isEnable) {
    return
  }

  if (isOneShotRunning.value) return

  const candidates = availableClickActions.value.filter(
    (name) => !!actions[name] || !!customActions[name]
  )
  if (candidates.length === 0) {
    console.warn('No available click actions found in model actions.')
    return
  }
  const actionName = candidates[Math.floor(Math.random() * candidates.length)]

  const run = async () => {
    isOneShotRunning.value = true
    try {
      if (isPlaying.value) {
        if (currentLoopAction.value) currentLoopAction.value.stop()
      }

      const action = actions[actionName]
      if (action) {
        await playGltfOneShot(action)
      } else if (customActions[actionName]) {
        await customActions[actionName]()
      }
    } finally {
      if (isPlaying.value) {
        if (currentLoopAction.value) currentLoopAction.value.play()
      }
      isOneShotRunning.value = false
    }
  }

  run()
}
</script>
