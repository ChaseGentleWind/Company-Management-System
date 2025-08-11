<template>
  <a-page-header :title="`订单详情: ${order?.order_uid || ''}`" @back="() => router.back()">
    <template #extra>
      <a-space>
        <a-button v-if="actions.canCancelOrder.value" @click="$emit('update-status', OrderStatus.CANCELLED)" danger>
          取消订单
        </a-button>
        <a-button v-if="actions.canRevertToDev.value" @click="$emit('update-status', OrderStatus.IN_DEVELOPMENT)">
          返工
        </a-button>
        <a-button
          v-if="actions.canSettleByTech.value"
          @click="$emit('update-status', OrderStatus.PENDING_SETTLEMENT)"
          type="primary"
        >
          确认可结算
        </a-button>
      </a-space>
    </template>
  </a-page-header>
</template>

<script setup lang="ts">
// ✨ Bug修复：从 'vue' 中导入 'computed'
import { type PropType, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useOrderActions } from '@/composables/useOrderActions'
import { type Order, OrderStatus } from '@/services/types'
import { PageHeader as APageHeader, Space as ASpace, Button as AButton } from 'ant-design-vue'

const props = defineProps({
  order: {
    type: Object as PropType<Order | null>,
    required: true
  }
})

defineEmits(['update-status'])

const router = useRouter()
const actions = useOrderActions(computed(() => props.order))
</script>
