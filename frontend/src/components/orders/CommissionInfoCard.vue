<template>
  <a-card v-if="myCommissionAmount !== null" title="我的本单提成" size="small">
    <a-statistic
      :value="myCommissionAmount"
      :precision="2"
      suffix="元"
      :value-style="{ color: '#3f8600', fontSize: '24px' }"
    >
      <template #prefix>
        <TrophyOutlined />
      </template>
    </a-statistic>
    <div style="color: #888; font-size: 12px; margin-top: 8px;">
      * 提成在订单状态变为“已核验”后生成
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { type Order, OrderStatus } from '@/services/types';
import { TrophyOutlined } from '@ant-design/icons-vue';
import { Card as ACard, Statistic as AStatistic } from 'ant-design-vue';

const props = defineProps({
  // 接收完整的订单对象作为 prop
  order: {
    type: Object as PropType<Order>,
    required: true
  }
});

const authStore = useAuthStore();
// 从 Pinia store 中获取当前登录用户的ID
const currentUserId = computed(() => (authStore.user?.sub ? parseInt(authStore.user.sub, 10) : null));

// 核心计算属性：决定是否显示以及显示多少金额
const myCommissionAmount = computed(() => {
  // 1. 检查订单状态是否已经过了提成计算节点
  if (![OrderStatus.VERIFIED, OrderStatus.SETTLED].includes(props.order.status)) {
    return null; // 状态不符，不显示
  }

  // 2. 检查当前用户ID是否存在
  if (currentUserId.value === null) {
      return null;
  }

  // 3. 在订单的 commissions 数组中查找属于当前用户的提成记录
  const myCommissionRecord = props.order.commissions.find(
    commission => commission.user_id === currentUserId.value
  );

  // 4. 如果找到了，返回提成金额；否则返回null
  return myCommissionRecord ? myCommissionRecord.amount : null;
});
</script>
