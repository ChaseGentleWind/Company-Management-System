<template>
  <a-modal
    :open="open"
    :title="result.title"
    :width="700"
    @update:open="$emit('update:open', $event)"
    @ok="$emit('update:open', false)"
  >
    <p>以下是导入失败的行和原因:</p>
    <div
      style="
        max-height: 300px;
        overflow-y: auto;
        margin-top: 10px;
        background: #f5f5f5;
        padding: 10px;
        border-radius: 4px;
      "
    >
      <p v-for="(error, index) in result.errors" :key="index" style="margin: 0 0 5px 0">
        {{ error }}
      </p>
    </div>
    <template #footer>
      <a-button type="primary" @click="$emit('update:open', false)">
        我知道了
      </a-button>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { Modal as AModal, Button as AButton } from 'ant-design-vue'
import type { PropType } from 'vue'

// 定义接收的数据结构
interface ImportResult {
  title: string
  errors: string[]
}

defineProps({
  open: {
    type: Boolean,
    required: true
  },
  result: {
    type: Object as PropType<ImportResult>,
    required: true
  }
})

defineEmits(['update:open'])
</script>
