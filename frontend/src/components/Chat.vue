<template>
  <div class="flex h-full relative">
    <!-- Боковая панель -->
    <Sidebar 
      :user="user" 
      :is-mobile="isMobile"
      :is-open="sidebarOpen"
      @close-sidebar="sidebarOpen = false"
    />
    
    <!-- Основная область чата -->
    <div class="flex-1 bg-gray-50 h-full relative flex flex-col">
      <!-- Мобильная шапка -->
      <div class="lg:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between flex-shrink-0">
        <button 
          @click="sidebarOpen = true"
          class=" text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg flex"
        >
          <i class="pi pi-bars"></i>
        </button>
        <h1 class="text-lg font-semibold text-gray-800 truncate">
          {{ currentChatTitle }}
        </h1>
        <div class="w-10"></div> <!-- Spacer для центрирования -->
      </div>

      <!-- Область сообщений -->
      <div class="flex-1 overflow-hidden">
        <ChatMessages />
      </div>
      
      <!-- Поле ввода -->
      <div class="flex-shrink-0">
        <ChatInput />
      </div>
    </div>

    <!-- Мобильный оверлей -->
    <div 
      v-if="isMobile && sidebarOpen"
      @click="sidebarOpen = false"
      class="fixed inset-0 bg-opacity-50 z-40 lg:hidden"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Sidebar from './Sidebar.vue'
import ChatMessages from './ChatMessages.vue'
import ChatInput from './ChatInput.vue'
import { useChatStore } from '@/stores/chatStore'

interface User {
  name: string
}

const user = ref<User>({ name: 'Пользователь' })
const chatStore = useChatStore()
const sidebarOpen = ref(false)
const isMobile = ref(false)

// Определяем текущий заголовок чата
const currentChatTitle = computed(() => {
  const chat = chatStore.currentChat
  return chat?.title || 'Выберите чат'
})

// Проверка размера экрана
const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 1024 // lg breakpoint
  if (!isMobile.value) {
    sidebarOpen.value = false
  }
}

// Обработчики событий
onMounted(() => {
  chatStore.loadChats()
  
  if (chatStore.chats.length === 0) {
    chatStore.createChat()
  }
  
  // Проверяем размер экрана
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  
  // Автосохранение
  window.addEventListener('beforeunload', () => {
    chatStore.saveChats()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// Закрытие сайдбара при выборе чата на мобильных
const handleChatSelect = (chatId: string) => {
  chatStore.selectChat(chatId)
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}
</script>
