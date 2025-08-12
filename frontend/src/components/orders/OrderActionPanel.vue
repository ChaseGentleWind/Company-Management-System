<template>
  <div class="sidebar">
    <template v-if="order">
      <finance-summary-card
        v-if="actions.isFinance.value && [OrderStatus.PENDING_SETTLEMENT, OrderStatus.VERIFIED].includes(order.status)"
        :order="order"
        style="margin-bottom: 16px;"
      />

      <a-card v-if="!order.is_locked || actions.isSuperAdmin.value" title="下一步操作">
        <a-space direction="vertical" style="width: 100%">

          <div v-if="actions.isCS.value && !order.is_locked">
            <a-button v-if="order.status === OrderStatus.PENDING_ASSIGNMENT" @click="emit('update-status', OrderStatus.PENDING_PAYMENT)" type="primary" block>更新为 [待付款]</a-button>
            <a-button v-if="order.status === OrderStatus.PENDING_PAYMENT" @click="emit('update-status', OrderStatus.PAID)" type="primary" block>确认收款 (进入已付款)</a-button>
            <a-button v-if="order.status === OrderStatus.PAID" @click="emit('update-status', OrderStatus.IN_DEVELOPMENT)" type="primary" block>分配技术/开始开发</a-button>
            <a-button v-if="order.status === OrderStatus.IN_DEVELOPMENT" @click="emit('update-status', OrderStatus.SHIPPED)" type="primary" block>更新为 [已发货]</a-button>
            <a-button v-if="order.status === OrderStatus.SHIPPED" @click="emit('update-status', OrderStatus.RECEIVED)" type="primary" block>确认 [已收货]</a-button>
          </div>

          <div v-if="actions.isTech.value">
            <a-button
              v-if="actions.canSettleByTech.value"
              @click="emit('update-status', OrderStatus.PENDING_SETTLEMENT)"
              type="primary"
              block
            >
              确认可结算 (进入待审核)
            </a-button>
          </div>

          <div v-if="actions.isFinance.value">
            <a-button v-if="order.status === OrderStatus.PENDING_SETTLEMENT" @click="emit('update-status', OrderStatus.VERIFIED)" type="primary" block>审核通过 (进入已核验)</a-button>
            <a-button v-if="order.status === OrderStatus.VERIFIED" @click="emit('update-status', OrderStatus.SETTLED)" type="primary" block style="background-color: #52c41a; border-color: #52c41a;">确认结算 (完成订单)</a-button>
          </div>

          <a-divider>其他操作</a-divider>
          <a-button v-if="actions.isCS.value" @click="emit('open-price-modal')" block>修改价格</a-button>
          <a-button v-if="actions.isCS.value" @click="emit('open-assign-modal')" block>分配/修改技术负责人</a-button>
          <a-button v-if="actions.canSetSpecialCommission.value" @click="emit('open-commission-modal')" block danger>设置特殊提成</a-button>
        </a-space>
      </a-card>

      <a-card v-if="order.is_locked && !actions.isSuperAdmin.value" title="订单已锁定">
        <a-alert message="此订单已结算或已取消，无法进行任何操作。" type="warning" show-icon />
      </a-card>

      <add-work-log-form
        v-if="actions.canAddWorkLog.value"
        :order-id="order.id"
        @log-added="emit('reload-order')"
        style="margin-top: 16px"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue';
import { useOrderActions } from '@/composables/useOrderActions';
import { type Order, OrderStatus } from '@/services/types';
import AddWorkLogForm from './AddWorkLogForm.vue';
import FinanceSummaryCard from './FinanceSummaryCard.vue';
import { Card as ACard, Space as ASpace, Button as AButton, Divider as ADivider, Alert as AAlert } from 'ant-design-vue';

const props = defineProps({
  order: {
    type: Object as PropType<Order | null>,
    required: true
  }
});

const emit = defineEmits(['update-status', 'open-price-modal', 'open-assign-modal', 'reload-order', 'open-commission-modal']);

const actions = useOrderActions(computed(() => props.order));
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
