<template>
  <div>
    <order-detail-header :order="order" @update-status="handleUpdateStatus" />

    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <div v-if="!loading && order" class="content-grid">
      <div class="main-content">
        <order-info-card :order="order" />
        <commission-info-card :order="order" />
        <work-log-timeline :logs="order.logs" />
      </div>

      <order-action-panel
        :order="order"
        @update-status="handleUpdateStatus"
        @open-price-modal="openPriceModal"
        @open-assign-modal="openAssignTechModal"
        @reload-order="fetchOrder"
        @open-commission-modal="openCommissionModal"
      />
    </div>

    <a-modal v-model:visible="isPriceModalVisible" title="修改订单价格" @ok="handleUpdatePrice">
      <a-form layout="vertical">
        <a-form-item label="新的订单价格 (元)">
          <a-input-number v-model:value="newPrice" style="width: 100%" :min="0" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:visible="isCommissionModalVisible" title="设置特殊提成" @ok="handleSetCommission">
      <p style="margin-bottom: 16px; color: #888;">此处设置的比例将仅对本订单生效，覆盖用户的默认提成比例。留空则表示不设置特殊比例。</p>
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
            placeholder="请选择"
            :loading="devsLoading"
            show-search
            :filter-option="(input: string, option: any) => option.children[0].children.toLowerCase().indexOf(input.toLowerCase()) >= 0"
          >
            <a-select-option v-for="dev in developers" :key="dev.id" :value="dev.id">
              {{ dev.full_name || dev.username }} (擅长: {{ dev.skills?.join(', ') || '未填写' }})
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { orderService } from '@/services/orderService';
import { userService } from '@/services/userService';
import { type Order, OrderStatus, type User } from '@/services/types';
import { message, Modal as AModal, Select as ASelect, SelectOption as ASelectOption, InputNumber as AInputNumber, Form as AForm, FormItem as AFormItem, Spin as ASpin } from 'ant-design-vue';

// --- 异步加载子组件，优化初始加载性能 ---
const OrderDetailHeader = defineAsyncComponent(() => import('@/components/orders/OrderDetailHeader.vue'));
const OrderInfoCard = defineAsyncComponent(() => import('@/components/orders/OrderInfoCard.vue'));
const WorkLogTimeline = defineAsyncComponent(() => import('@/components/orders/WorkLogTimeline.vue'));
const OrderActionPanel = defineAsyncComponent(() => import('@/components/orders/OrderActionPanel.vue'));
const CommissionInfoCard = defineAsyncComponent(() => import('@/components/orders/CommissionInfoCard.vue'));

const route = useRoute();
const orderId = Number(route.params.id);

// --- 状态管理 ---
const order = ref<Order | null>(null);
const loading = ref(true);

// --- 数据获取 ---
const fetchOrder = async () => {
  loading.value = true;
  try {
    order.value = await orderService.getOrderById(orderId);
  } catch (error) {
    message.error('获取订单详情失败');
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

const handleUpdatePrice = async () => {
  if (!order.value || newPrice.value === undefined) return message.warn('请输入有效的价格');
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
  if (!order.value || selectedTechId.value === undefined) return message.warn('请选择一位技术人员');
  try {
    await orderService.updateOrderDetails(order.value.id, { developer_id: selectedTechId.value });
    message.success('技术负责人已更新');
    isAssignModalVisible.value = false;
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || '分配失败');
  }
};

const isCommissionModalVisible = ref(false);
// 使用 reactive 来管理表单数据
const commissionForm = reactive({
  cs_rate: undefined as number | undefined,
  tech_rate: undefined as number | undefined,
});

const openCommissionModal = () => {
  // 从当前订单数据初始化表单的默认值
  const override_rates = order.value?.commission_rate_override;
  // 使用 ?? (空值合并操作符) 来处理 null 或 undefined 的情况
  commissionForm.cs_rate = override_rates?.cs_rate ?? undefined;
  commissionForm.tech_rate = override_rates?.tech_rate ?? undefined;
  isCommissionModalVisible.value = true;
};

const handleSetCommission = async () => {
  if (!order.value) return;
  try {
    // 构造一个只包含已定义值（非undefined）的对象
    const payload: { cs_rate?: number; tech_rate?: number } = {};
    if (commissionForm.cs_rate !== undefined) payload.cs_rate = commissionForm.cs_rate;
    if (commissionForm.tech_rate !== undefined) payload.tech_rate = commissionForm.tech_rate;

    await orderService.setCommissionOverride(order.value.id, payload);
    message.success('特殊提成设置成功');
    isCommissionModalVisible.value = false;
    await fetchOrder(); // 重新获取订单数据以更新视图
  } catch (error: any) {
    message.error(error.response?.data?.msg || '设置失败');
  }
};

</script>

<style scoped>
.loading-container {
  text-align: center;
  padding: 50px;
}
.content-grid {
  display: grid;
  grid-template-columns: 3fr 1fr; /* 主内容区 : 侧边栏 */
  gap: 16px;
  padding: 0 24px;
}
.main-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
@media (max-width: 992px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
