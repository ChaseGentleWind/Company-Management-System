<template>
  <a-card title="财务结算摘要" :bordered="false" style="background-color: #fafafa;">
    <a-descriptions :column="1" layout="horizontal" bordered size="small">

      <a-descriptions-item label="订单总金额">
        <span style="font-weight: bold; color: #d48806;">{{ order.final_price ?? 'N/A' }} 元</span>
      </a-descriptions-item>

      <a-descriptions-item :label="`客服提成 (${order.creator.full_name})`">
        <span style="font-weight: bold; color: #3f8600;">{{ cs_commission?.amount ?? 0 }} 元</span>
      </a-descriptions-item>
      <a-descriptions-item label="客服收款账号">
        <div v-if="order.creator?.financial_account">
          <CopyOutlined @click="copyToClipboard(order.creator.financial_account)" style="cursor: pointer; color: #1890ff; margin-right: 8px;" />
          <span>{{ order.creator.financial_account }}</span>
        </div>
        <a-tag v-else color="warning">未提供</a-tag>
      </a-descriptions-item>

      <template v-if="order.developer">
        <a-descriptions-item :label="`技术提成 (${order.developer.full_name})`">
           <span style="font-weight: bold; color: #3f8600;">{{ tech_commission?.amount ?? 0 }} 元</span>
        </a-descriptions-item>
        <a-descriptions-item label="技术收款账号">
          <div v-if="order.developer.financial_account">
            <CopyOutlined @click="copyToClipboard(order.developer.financial_account)" style="cursor: pointer; color: #1890ff; margin-right: 8px;" />
            <span>{{ order.developer.financial_account }}</span>
          </div>
          <a-tag v-else color="warning">未提供</a-tag>
        </a-descriptions-item>
      </template>

    </a-descriptions>
  </a-card>
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue';
import { type Order, type Commission, UserRole } from '@/services/types';
import { Card as ACard, Descriptions as ADescriptions, DescriptionsItem as ADescriptionsItem, Tag as ATag, message } from 'ant-design-vue';
import { CopyOutlined } from '@ant-design/icons-vue';

const props = defineProps({
  order: {
    type: Object as PropType<Order>,
    required: true
  }
});

// 计算客服的提成记录
const cs_commission = computed<Commission | undefined>(() => {
  return props.order.commissions.find(c => c.role_at_time === UserRole.CUSTOMER_SERVICE);
});

// 计算技术的提成记录
const tech_commission = computed<Commission | undefined>(() => {
  return props.order.commissions.find(c => c.role_at_time === UserRole.DEVELOPER);
});

// 实现点击复制到剪贴板功能
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板！');
  } catch (err) {
    message.error('复制失败');
  }
};
</script>
