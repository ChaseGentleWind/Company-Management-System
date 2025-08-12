<template>
  <div v-if="loading" class="loading-container">
    <a-spin size="large" tip="正在加载订单详情..." />
  </div>

  <div v-else-if="!order" class="loading-container">
     <a-empty description="未找到该订单或您没有权限访问" />
  </div>

  <div v-else>
    <a-card :bordered="false" style="margin-bottom: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 500;">
          订单详情: {{ order.order_uid }}
        </span>
      </template>
      <template #extra>
        <a-space>
          <a-button
            v-if="actions.canRevertToDev.value"
            @click="handleUpdateStatus(OrderStatus.IN_DEVELOPMENT)"
          >
            返工
          </a-button>
          <a-button
            v-if="actions.canSettleByTech.value"
            @click="handleUpdateStatus(OrderStatus.PENDING_SETTLEMENT)"
            type="primary"
          >
            确认可结算
          </a-button>
           <a-button
            v-if="actions.canCancelOrder.value"
            @click="handleUpdateStatus(OrderStatus.CANCELLED)"
            danger
          >
            取消订单
          </a-button>
        </a-space>
      </template>

      <div class="content-grid">
        <div class="main-content">
          <order-info-card :order="order" />
        </div>
        <div class="sidebar">
           <order-action-panel
            :order="order"
            @update-status="handleUpdateStatus"
            @open-price-modal="openPriceModal"
            @open-assign-modal="openAssignTechModal"
            @reload-order="fetchOrder"
            @open-commission-modal="openCommissionModal"
          />
        </div>
      </div>
    </a-card>

    <a-row :gutter="24">
      <a-col :xs="24" :lg="16">
        <work-log-timeline :logs="order.logs" />
      </a-col>
      <a-col :xs="24" :lg="8">
        <commission-info-card :order="order" />
      </a-col>
    </a-row>
  </div>

  <a-modal v-model:visible="isPriceModalVisible" title="修改订单价格" @ok="handleUpdatePrice">
    <a-form layout="vertical">
      <a-form-item label="新的订单价格 (元)">
        <a-input-number v-model:value="newPrice" style="width: 100%" :min="0" addon-after="元" />
      </a-form-item>
    </a-form>
  </a-modal>

  <a-modal v-model:visible="isCommissionModalVisible" title="设置特殊提成" @ok="handleSetCommission">
    <p style="margin-bottom: 16px; color: rgba(0, 0, 0, 0.45);">
      此处设置的比例将仅对本订单生效，覆盖用户的默认提成比例。留空则表示不设置特殊比例。
    </p>
    <a-form layout="vertical">
      <a-form-item v-if="order?.creator" :label="`客服提成率 (%) - ${order.creator.full_name}`">
        <a-input-number v-model:value="commissionForm.cs_rate" style="width: 100%" :min="0" :max="100" placeholder="例如: 10.5"/>
      </a-form-item>
      <a-form-item v-if="order?.developer" :label="`技术提成率 (%) - ${order.developer.full_name}`">
        <a-input-number v-model:value="commissionForm.tech_rate" style="width: 100%" :min="0" :max="100" placeholder="例如: 12"/>
      </a-form-item>
    </a-form>
  </a-modal>

  <a-modal v-model:visible="isAssignModalVisible" title="分配技术负责人" @ok="handleAssignTech">
    <a-form layout="vertical">
      <a-form-item label="选择技术人员">
        <a-select
          v-model:value="selectedTechId"
          style="width: 100%"
          placeholder="请搜索或选择技术人员"
          :loading="devsLoading"
          show-search
          :filter-option="(input: string, option: any) => option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0"
        >
          <a-select-option v-for="dev in developers" :key="dev.id" :value="dev.id" :label="dev.full_name || dev.username">
            {{ dev.full_name || dev.username }} (擅长: {{ dev.skills?.join(', ') || '未填写' }})
          </a-select-option>
        </a-select>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent, reactive, computed } from 'vue';
import { useRoute } from 'vue-router';
import { orderService } from '@/services/orderService';
import { userService } from '@/services/userService';
import { type Order, OrderStatus, type User } from '@/services/types';
import { useOrderActions } from '@/composables/useOrderActions';
import {
  message,
  Modal as AModal,
  Select as ASelect,
  SelectOption as ASelectOption,
  InputNumber as AInputNumber,
  Form as AForm,
  FormItem as AFormItem,
  Spin as ASpin,
  Card as ACard,
  Space as ASpace,
  Button as AButton,
  Row as ARow,
  Col as ACol,
  Empty as AEmpty,
} from 'ant-design-vue';

// --- 异步加载子组件，优化初始加载性能 ---
const OrderInfoCard = defineAsyncComponent(() => import('@/components/orders/OrderInfoCard.vue'));
const WorkLogTimeline = defineAsyncComponent(() => import('@/components/orders/WorkLogTimeline.vue'));
const OrderActionPanel = defineAsyncComponent(() => import('@/components/orders/OrderActionPanel.vue'));
const CommissionInfoCard = defineAsyncComponent(() => import('@/components/orders/CommissionInfoCard.vue'));

const route = useRoute();
const orderId = Number(route.params.id);

// --- 状态管理 ---
const order = ref<Order | null>(null);
const loading = ref(true);

const actions = useOrderActions(computed(() => order.value));

// --- 数据获取 ---
const fetchOrder = async () => {
  loading.value = true;
  try {
    order.value = await orderService.getOrderById(orderId);
  } catch (error) {
    console.error("Failed to fetch order:", error);
    message.error('获取订单详情失败');
    order.value = null; // 获取失败时清空订单
  } finally {
    loading.value = false;
  }
};

onMounted(fetchOrder);

// --- 事件处理器 ---
const handleUpdateStatus = async (targetStatus: OrderStatus) => {
  if (!order.value) return;
  try {
    const res = await orderService.updateOrderStatus(order.value.id, targetStatus);
    message.success(res.message);
    await fetchOrder(); // 重新获取数据以更新整个视图
  } catch (error: any) {
    message.error(error.response?.data?.msg || '更新状态失败');
  }
};

// --- 模态框逻辑 ---
const isPriceModalVisible = ref(false);
const newPrice = ref<number | undefined>(undefined);
const isAssignModalVisible = ref(false);
const devsLoading = ref(false);
const developers = ref<User[]>([]);
const selectedTechId = ref<number | undefined>(undefined);
const isCommissionModalVisible = ref(false);

const commissionForm = reactive({
  cs_rate: undefined as number | undefined,
  tech_rate: undefined as number | undefined,
});

const openPriceModal = () => {
  newPrice.value = order.value?.final_price;
  isPriceModalVisible.value = true;
};

const openAssignTechModal = async () => {
  isAssignModalVisible.value = true;
  devsLoading.value = true;
  try {
    developers.value = await userService.getAvailableDevelopers();
    selectedTechId.value = order.value?.developer?.id;
  } catch (error) {
    message.error('获取技术人员列表失败');
  } finally {
    devsLoading.value = false;
  }
};

const openCommissionModal = () => {
  const override_rates = order.value?.commission_rate_override;
  commissionForm.cs_rate = override_rates?.cs_rate ?? undefined;
  commissionForm.tech_rate = override_rates?.tech_rate ?? undefined;
  isCommissionModalVisible.value = true;
};

const handleUpdatePrice = async () => {
  if (!order.value || newPrice.value === undefined || newPrice.value < 0) {
      return message.warn('请输入有效的价格');
  }
  try {
    await orderService.updateOrderDetails(order.value.id, { final_price: newPrice.value });
    message.success('价格更新成功');
    isPriceModalVisible.value = false;
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || '价格更新失败');
  }
};

const handleAssignTech = async () => {
  if (!order.value || selectedTechId.value === undefined) {
      return message.warn('请选择一位技术人员');
  }
  try {
    await orderService.updateOrderDetails(order.value.id, { developer_id: selectedTechId.value });
    message.success('技术负责人已更新');
    isAssignModalVisible.value = false;
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || '分配失败');
  }
};

const handleSetCommission = async () => {
  if (!order.value) return;
  try {
    const payload: { cs_rate?: number; tech_rate?: number } = {};
    if (commissionForm.cs_rate !== undefined && commissionForm.cs_rate !== null) payload.cs_rate = commissionForm.cs_rate;
    if (commissionForm.tech_rate !== undefined && commissionForm.tech_rate !== null) payload.tech_rate = commissionForm.tech_rate;

    await orderService.setCommissionOverride(order.value.id, payload);
    message.success('特殊提成设置成功');
    isCommissionModalVisible.value = false;
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || '设置失败');
  }
};
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr; /* 主内容区 : 侧边栏 */
  gap: 24px;
}
.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
@media (max-width: 992px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
