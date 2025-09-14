import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface Chat {
  id: string
  title: string
  updatedAt: Date
  messages: Message[]
}

export const useChatStore = defineStore('chat', () => {
  const chats = ref<Chat[]>([])
  const activeChatId = ref<string | null>(null)
  const isLoading = ref(false)

  const currentChat = computed(() => 
    chats.value.find(c => c.id === activeChatId.value)
  )

  const currentMessages = computed(() => 
    currentChat.value?.messages || []
  )

  const createChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'Новый чат',
      updatedAt: new Date(),
      messages: []
    }
    chats.value.unshift(newChat)
    activeChatId.value = newChat.id
    return newChat
  }

  const selectChat = (chatId: string) => {
    activeChatId.value = chatId
  }

  const deleteChat = (chatId: string) => {
    const index = chats.value.findIndex(c => c.id === chatId)
    if (index > -1) {
      chats.value.splice(index, 1)
      if (activeChatId.value === chatId) {
        activeChatId.value = chats.value[0]?.id || null
      }
    }
  }

  const sendMessage = async (content: string) => {
    if (!activeChatId.value) return

    const chat = chats.value.find(c => c.id === activeChatId.value)
    if (!chat) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    }

    chat.messages.push(userMessage)
    chat.updatedAt = new Date()

    if (chat.title === 'Новый чат') {
      chat.title = content.slice(0, 30) + (content.length > 30 ? '...' : '')
    }

    isLoading.value = true

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, chatId: activeChatId.value })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }

      chat.messages.push(assistantMessage)
      chat.updatedAt = new Date()
    } catch (error) {
      console.error('Ошибка отправки сообщения:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.',
        timestamp: new Date()
      }
      
      chat.messages.push(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const loadChats = () => {
    const saved = localStorage.getItem('chat-chats')
    if (saved) {
      try {
        const parsedChats = JSON.parse(saved)
        chats.value = parsedChats.map((chat: any) => ({
          ...chat,
          updatedAt: new Date(chat.updatedAt),
          messages: chat.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }))
      } catch (error) {
        console.error('Ошибка загрузки чатов:', error)
      }
    }
  }

  const saveChats = () => {
    localStorage.setItem('chat-chats', JSON.stringify(chats.value))
  }

  return {
    chats,
    activeChatId,
    isLoading,
    currentChat,
    currentMessages,
    createChat,
    selectChat,
    deleteChat,
    sendMessage,
    loadChats,
    saveChats
  }
})
