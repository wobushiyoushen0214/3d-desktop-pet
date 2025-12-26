<!--
 * @Author: LiZhiWei
 * @Date: 2025-12-23 14:53:55
 * @LastEditors: LiZhiWei
 * @LastEditTime: 2025-12-26 10:00:04
 * @Description: 
-->
<template>
  <SubWindowLayout title="宠物管理">
    <div class="p-6">
      <div class="grid grid-cols-2 gap-4">
        <div
          v-for="pet in petList"
          :key="pet.id"
          class="group relative flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer overflow-visible"
          :class="[
            currentPetId === pet.id 
              ? 'border-blue-500 bg-blue-50/30 shadow-md transform scale-[1.02]' 
              : 'border-gray-100 hover:border-blue-200 bg-white hover:shadow-lg hover:-translate-y-1'
          ]"
          @click="switchPet(pet.id)"
        >
          <!-- 选中状态 -->
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="transform scale-0 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-0 opacity-0"
          >
            <div 
              v-if="currentPetId === pet.id"
              class="absolute -top-2.5 -right-2.5 w-7 h-7 bg-blue-500 rounded-full flex items-center justify-center text-white shadow-lg z-20 border-2 border-white"
            >
              <span class="text-sm font-bold">✓</span>
            </div>
          </Transition>

          <!-- 宠物预览图 -->
          <div 
            class="w-full aspect-square rounded-lg bg-gray-50 mb-4 flex items-center justify-center transition-transform duration-500 group-hover:scale-110"
            :class="currentPetId === pet.id ? 'bg-white' : ''"
          >
            <!-- 自动识别预览类型：图片路径 (包含 .) 还是文字表情 -->
            <img 
              v-if="pet.preview && (pet.preview.includes('.') || pet.preview.startsWith('http'))" 
              :src="pet.preview" 
              class="w-full h-full object-contain p-2" 
            />
            <span v-else class="text-5xl">
              {{ pet.preview || '🐾' }}
            </span>
          </div>

          <!-- 宠物名称 -->
          <span class="font-bold text-gray-800 text-lg mb-1">{{ pet.name }}</span>
          
          <!-- 动作列表简介 -->
          <div class="mt-2 flex flex-wrap gap-1.5 justify-center">
            <span 
              v-for="action in pet.availableClickActions" 
              :key="action"
              class="px-2 py-0.5 bg-gray-100 text-[11px] text-gray-500 rounded-full border border-gray-200/50"
            >
              {{ action }}
            </span>
          </div>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="mt-8 text-center text-sm text-gray-400">
        点击卡片即可切换桌面宠物
      </div>
    </div>
  </SubWindowLayout>
</template>

<script setup lang="ts">
import SubWindowLayout from '../components/SubWindowLayout.vue'
import { useModel, petList } from '../composable/useModel'

const { currentPetId, switchPet } = useModel()
</script>

<style scoped>
.grid {
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
}
</style>
