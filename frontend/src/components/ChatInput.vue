<template>
  <div class="p-4">
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-2xl sm:rounded-3xl shadow-lg border border-gray-200 p-3 sm:p-4">
        <div class="flex flex-col">
          <div class="relative">
            <textarea
              id="message-input"
              v-model="message"
              @keydown="handleKeyDown"
              :disabled="chatStore.isLoading"
              rows="5"
              cols=""
              class="w-full px-3 pt-4 pb-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[40px] transition-all duration-200 disabled:bg-gray-100 disabled:cursor-not-allowed"
              style="resize: none; min-height: 40px;"
            />
            <label 
              for="message-input" 
              class="absolute left-4 transition-all duration-200 pointer-events-none"
              :class="message ? 'hidden' : 'top-4 text-gray-500'"
            >
              Введите сообщение...
            </label>
          </div>

          <!-- Панель управления -->
          <div class="flex justify-end items-center mt-2">
            <Button
              @click="sendMessage"
              :disabled="!message.trim() || chatStore.isLoading"
              icon="pi pi-arrow-right"
              size="small"
              class="!bg-blue-600 !hover:bg-blue-700 !rounded-full !text-white sm:!h-10 sm:!w-10 !h-8 !w-8 !text-sm sm:!text-base"
              rounded
              :severity="chatStore.isLoading ? 'info' : 'primary'"
              :loading="chatStore.isLoading"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import Button from 'primevue/button'

const message = ref('')
const chatStore = useChatStore()

const sendMessage = () => {
  if (!message.value.trim() || chatStore.isLoading) return

  if (!chatStore.activeChatId) {
    chatStore.createChat()
  }

  chatStore.sendMessage(message.value.trim())
  message.value = ''
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}
</script>
