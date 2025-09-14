<template>
  <div ref="messagesContainer" class="h-full overflow-y-auto p-4 sm:p-6 sm:px-20 space-y-4 bg-gray-50">
    <!-- Пустое состояние -->
    <div v-if="chatStore.currentMessages.length === 0 && !chatStore.isLoading" 
         class="flex items-center justify-center h-full">
      <div class="text-center text-gray-500 max-w-md mx-auto px-4">
        <i class="pi pi-comments text-6xl mb-6 text-gray-300"></i>
        <h3 class="text-xl font-medium text-gray-700 mb-2">Начните новый разговор</h3>
        <p class="text-sm text-gray-500">Задайте вопрос или попросите помочь с задачей</p>
      </div>
    </div>

    <!-- Сообщения -->
    <div 
      v-for="message in chatStore.currentMessages" 
      :key="message.id"
      class="flex gap-3 sm:gap-4"
      :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
    >
      <div 
        class="max-w-[85%] sm:max-w-3xl rounded-2xl px-3 sm:px-4 py-3 shadow-sm"
        :class="message.role === 'user' 
          ? 'bg-blue-500 text-white' 
          : 'bg-white text-gray-800 border border-gray-200'"
      >
        <div class="whitespace-pre-wrap text-sm sm:text-base leading-relaxed">
          {{ message.content }}
        </div>
        <div class="text-xs mt-2 flex justify-end"
             :class="message.role === 'user' ? 'text-blue-100' : 'text-gray-500'">
          {{ formatTime(message.timestamp) }}
        </div>
      </div>
    </div>
    
    <!-- Индикатор загрузки -->
    <div v-if="chatStore.isLoading" class="flex justify-start">
      <div class="bg-white text-gray-800 rounded-2xl px-4 py-3 border border-gray-200 shadow-sm">
        <div class="flex items-center gap-2">
          <div class="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full"></div>
          <span class="text-sm">AI печатает...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chatStore'

const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement>()

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(
  () => chatStore.currentMessages.length,
  () => {
    scrollToBottom()
  }
)

watch(
  () => chatStore.isLoading,
  (isLoading) => {
    if (isLoading) {
      scrollToBottom()
    }
  }
)

const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>
