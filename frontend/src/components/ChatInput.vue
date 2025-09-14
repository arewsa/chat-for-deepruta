<template>
  <div class="p-4">
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-2xl sm:rounded-3xl shadow-lg border border-gray-200 p-3 sm:p-4">
        <div class="flex flex-col">
          <!-- Поле ввода -->
          <textarea
            ref="textareaRef"
            v-model="message"
            @keydown="handleKeyDown"
            @input="adjustHeight"
            placeholder="Введите сообщение..."
            class="flex-1 bg-transparent text-gray-800 placeholder-gray-400 resize-none outline-none text-sm sm:text-base leading-relaxed"
            :style="{ minHeight: '40px', maxHeight: '200px' }"
            :disabled="chatStore.isLoading"
          ></textarea>

          <!-- Панель управления -->
          <div class="flex justify-end items-center">
            <!-- Кнопка отправки -->
            <button
              @click="sendMessage"
              :disabled="!message.trim() || chatStore.isLoading"
              class="w-8 h-8 sm:w-8 sm:h-8 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-full flex items-center justify-center transition-colors"
            >
              <i class="pi pi-arrow-right text-white sm:text-sm" style="font-size: 0.5rem"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useChatStore } from '@/stores/chatStore'

const message = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const chatStore = useChatStore()

// Автоматическое изменение высоты textarea
const adjustHeight = async () => {
  await nextTick()
  if (textareaRef.value) {
    // Сбрасываем высоту для корректного расчета
    textareaRef.value.style.height = 'auto'

    // Получаем scrollHeight и устанавливаем новую высоту
    const scrollHeight = textareaRef.value.scrollHeight
    const minHeight = 40 // минимальная высота
    const maxHeight = 200 // максимальная высота

    // Ограничиваем высоту между min и max значениями
    const newHeight = Math.min(Math.max(scrollHeight, minHeight), maxHeight)
    textareaRef.value.style.height = `${newHeight}px`
  }
}

const sendMessage = () => {
  if (!message.value.trim() || chatStore.isLoading) return

  chatStore.sendMessage(message.value.trim())
  message.value = ''

  // Сбрасываем высоту после отправки
  if (textareaRef.value) {
    textareaRef.value.style.height = '40px'
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}
</script>
