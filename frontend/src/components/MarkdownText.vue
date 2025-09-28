<template>
  <div class="markdown-content" v-html="renderedMarkdown"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

interface Props {
  text: string
}

const props = defineProps<Props>()

const renderedMarkdown = computed(() => {
  return marked.parse(props.text)
})
</script>

    