<template>
  <div id="app" class="h-screen bg-gray-50 flex flex-col">
    <!-- Заголовок приложения -->
    <header class="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14 sm:h-16">
          <!-- Логотип и название -->
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-lg sm:text-xl font-bold text-gray-900">
                <i class="pi pi-comments text-blue-500 mr-2"></i>
                <span class="hidden sm:inline">ChatForDeepRuta</span>
                <span class="sm:hidden">Chat</span>
              </h1>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Основной контент -->
    <main class="flex-1 overflow-hidden">
      <Chat />
    </main>
  </div>
</template>

<script setup lang="ts">
import Chat from './components/Chat.vue'
</script>
