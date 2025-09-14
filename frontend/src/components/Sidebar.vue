<template>
  <div 
    class="bg-white h-screen flex flex-col border-r border-gray-200 transition-all duration-300"
    :class="sidebarClasses"
  >
    <!-- Мобильная кнопка закрытия -->
    <div class="lg:hidden flex justify-between items-center p-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-800">Чаты</h2>
      <button 
        @click="$emit('close-sidebar')"
        class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
      >
        <i class="pi pi-times"></i>
      </button>
    </div>

    <!-- Кнопка нового чата -->
    <div class="p-4 border-b border-gray-200">
      <button 
        class="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg flex items-center justify-center gap-2 transition-colors text-sm font-medium"
        @click="chatStore.createChat()"
      >
        <i class="pi pi-plus"></i>
        <span class="hidden sm:inline">Новый чат</span>
        <span class="sm:hidden">Новый</span>
      </button>
    </div>
    
    <!-- Список чатов -->
    <div class="flex-1 overflow-y-auto p-2">
      <div class="space-y-1">
        <div 
          v-for="chat in chatStore.chats" 
          :key="chat.id"
          class="p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors group relative"
          :class="{ 'bg-blue-50 border border-blue-200': chatStore.activeChatId === chat.id }"
          @click="chatStore.selectChat(chat.id); $emit('close-sidebar')"
        >
          <div class="text-gray-800 text-sm truncate font-medium pr-8">
            {{ chat.title }}
          </div>
          <div class="text-gray-500 text-xs mt-1">
            {{ formatDate(chat.updatedAt) }}
          </div>
          
          <!-- Кнопка удаления -->
          <button 
            @click.stop="chatStore.deleteChat(chat.id)"
            class="absolute right-2 top-2 opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
            title="Удалить чат"
          >
            <i class="pi pi-trash text-red-500 text-xs"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Информация о пользователе -->
    <div class="p-4 border-t border-gray-200">
      <div class="flex items-center gap-3 text-gray-600">
        <i class="pi pi-user"></i>
        <span class="text-sm truncate">{{ user?.name || 'Пользователь' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chatStore'

interface User {
  name: string
}

const props = defineProps<{
  user?: User
  isMobile?: boolean
  isOpen?: boolean
}>()

defineEmits<{
  'close-sidebar': []
}>()

const chatStore = useChatStore()

const sidebarClasses = computed(() => {
  return {
    'w-full': true,
    'lg:w-1/4': true,
    'xl:w-1/5': true,
    'fixed lg:relative': true,
    'z-50 lg:z-auto': true,
    'transform lg:transform-none': true,
    'transition-transform duration-300': true,
    '-translate-x-full lg:translate-x-0': !props.isOpen && props.isMobile,
    'translate-x-0': props.isOpen || !props.isMobile
  }
})

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>
