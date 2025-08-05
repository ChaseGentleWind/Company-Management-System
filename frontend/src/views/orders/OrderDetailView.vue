<template>
  <div>
    <a-page-header :title="`订单详情: ${order?.order_uid || ''}`" @back="() => router.back()">
      <template #extra>
        <a-space>
          <a-button v-if="canCancelOrder" @click="handleStatusUpdate(OrderStatus.CANCELLED)" danger>
            取消订单
          </a-button>
          <a-button v-if="canRevertToDev" @click="handleStatusUpdate(OrderStatus.IN_DEVELOPMENT)">
            返工
          </a-button>
          <a-button
            v-if="isTechAndCanSettle"
            @click="handleStatusUpdate(OrderStatus.PENDING_SETTLEMENT)"
            type="primary"
          >
            确认可结算
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div v-if="loading" style="text-align: center; margin-top: 50px">
      <a-spin size="large" />
    </div>

    <div v-if="!loading && order" class="content-grid">
      <div class="main-content">
        <a-card title="订单信息">
          <a-descriptions bordered :column="2">
            <a-descriptions-item label="业务ID">{{ order.order_uid }}</a-descriptions-item>
            <a-descriptions-item label="订单状态">
              <a-tag :color="getStatusColor(order.status)">{{ order.status }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="客户姓名">{{
              order.customer_info.name
            }}</a-descriptions-item>
            <a-descriptions-item label="联系方式">{{
              order.customer_info.phone
            }}</a-descriptions-item>
            <a-descriptions-item label="最终价格"
              >{{ order.final_price ?? '未定价' }} 元</a-descriptions-item
            >
            <a-descriptions-item label="创建人(客服)">{{
              order.creator.full_name
            }}</a-descriptions-item>
            <a-descriptions-item label="负责人(技术)">{{
              order.developer?.full_name ?? '未分配'
            }}</a-descriptions-item>
            <a-descriptions-item label="创建时间">{{
              new Date(order.created_at).toLocaleString()
            }}</a-descriptions-item>
            <a-descriptions-item label="需求描述" :span="2">{{
              order.requirements_desc
            }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="工作日志" style="margin-top: 16px">
          <a-timeline v-if="order.logs.length > 0">
            <a-timeline-item v-for="log in order.logs" :key="log.id">
              <p>
                <strong>{{ log.developer.full_name }}</strong>
              </p>
              <p>{{ log.log_content }}</p>
              <p style="color: #888; font-size: 12px">
                {{ new Date(log.created_at).toLocaleString() }}
              </p>
            </a-timeline-item>
          </a-timeline>
          <a-empty v-else description="暂无工作日志" />
        </a-card>
      </div>

      <div class="sidebar">
        <a-card title="下一步操作" v-if="!order.is_locked">
          <a-space direction="vertical" style="width: 100%">
            <div v-if="isCS">
              <a-button
                v-if="order.status === OrderStatus.PENDING_ASSIGNMENT"
                @click="handleStatusUpdate(OrderStatus.PENDING_PAYMENT)"
                type="primary"
                block
              >
                更新为 [待付款]
              </a-button>

              <a-button
                v-if="order.status === OrderStatus.PENDING_PAYMENT"
                @click="handleStatusUpdate(OrderStatus.IN_DEVELOPMENT)"
                type="primary"
                block
              >
                确认收款，开始开发
              </a-button>

              <a-button
                v-if="order.status === OrderStatus.IN_DEVELOPMENT"
                @click="handleStatusUpdate(OrderStatus.SHIPPED)"
                type="primary"
                block
              >
                更新为 [已发货]
              </a-button>

              <a-button
                v-if="order.status === OrderStatus.SHIPPED"
                @click="handleStatusUpdate(OrderStatus.RECEIVED)"
                type="primary"
                block
              >
                确认 [已收货]
              </a-button>
            </div>

            <div v-if="isFinance">
              <a-button
                v-if="order.status === OrderStatus.PENDING_SETTLEMENT"
                @click="handleStatusUpdate(OrderStatus.VERIFIED)"
                type="primary"
                block
              >
                审核通过 (进入已核验)
              </a-button>
              <a-button
                v-if="order.status === OrderStatus.VERIFIED"
                @click="handleStatusUpdate(OrderStatus.SETTLED)"
                type="primary"
                block
                style="background-color: #52c41a; border-color: #52c41a;"
              >
                确认结算 (完成订单)
              </a-button>
            </div>
            <a-divider>其他操作</a-divider>
            <a-button v-if="isCS" @click="showPriceModal" block>修改价格</a-button>
            <a-button v-if="isCS" @click="showAssignTechModal" block
              >分配/修改技术负责人</a-button
            >
          </a-space>
        </a-card>
        <a-card v-if="order.is_locked" title="订单已锁定">
          <a-alert message="此订单已结算或已取消，无法进行任何操作。" type="warning" show-icon />
        </a-card>

        <a-card
          title="添加工作日志"
          style="margin-top: 16px"
          v-if="isAssignedDeveloper && !order.is_locked"
        >
          <a-form :model="logFormState" layout="vertical" @finish="handleLogSubmit">
            <a-form-item
              label="日志内容"
              name="log_content"
              :rules="[{ required: true, message: '日志内容不能为空' }]"
            >
              <a-textarea
                v-model:value="logFormState.log_content"
                :rows="4"
                placeholder="请填写工作进展..."
              />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="isLogSubmitting"
                >提交日志</a-button
              >
            </a-form-item>
          </a-form>
        </a-card>
      </div>
    </div>

    <a-modal v-model:visible="isPriceModalOpen" title="修改订单价格" @ok="handleUpdatePrice">
      <a-form layout="vertical">
        <a-form-item label="新的订单价格 (元)">
          <a-input-number v-model:value="newPrice" style="width: 100%" :min="0" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="isAssignTechModalOpen"
      title="分配技术负责人"
      @ok="handleAssignTech"
    >
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
              {{ dev.full_name || dev.username }} (擅长: {{ dev.skills?.join(', ') || '未填写'
              }})
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { orderService } from '@/services/orderService';
import { userService } from '@/services/userService';
import { type Order, OrderStatus, UserRole, type User } from '@/services/types';
import {
  message,
  Modal as AModal,
  Select as ASelect,
  SelectOption as ASelectOption,
  InputNumber as AInputNumber,
  Form as AForm,
  FormItem as AFormItem,
  PageHeader as APageHeader,
  Spin as ASpin,
  Card as ACard,
  Descriptions as ADescriptions,
  DescriptionsItem as ADescriptionsItem,
  Tag as ATag,
  Button as AButton,
  Space as ASpace,
  Divider as ADivider,
  Alert as AAlert,
  Timeline as ATimeline,
  TimelineItem as ATimelineItem,
  Empty as AEmpty,
  Textarea as ATextarea,
} from 'ant-design-vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const orderId = Number(route.params.id);
const order = ref<Order | null>(null);
const loading = ref(true);

// 【警告修复】将所有 is...Visible 重命名为 is...Open (可选，但推荐)
const isPriceModalOpen = ref(false);
const newPrice = ref<number | undefined>(undefined);
const isAssignTechModalOpen = ref(false);
const devsLoading = ref(false);
const developers = ref<User[]>([]);
const selectedTechId = ref<number | undefined>(undefined);

// 【BUG修复关键区域】使用 reactive 对象管理表单状态
const logFormState = reactive({
  log_content: '',
});
const isLogSubmitting = ref(false);

const fetchOrder = async () => {
  loading.value = true;
  try {
    order.value = await orderService.getOrderById(orderId);
  } catch (error) {
    message.error('获取订单详情失败');
    router.back();
  } finally {
    loading.value = false;
  }
};

onMounted(fetchOrder);



const handleStatusUpdate = async (targetStatus: OrderStatus) => {
  if (!order.value) return;
  try {
    const res = await orderService.updateOrderStatus(order.value.id, targetStatus);
    message.success(res.message);
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || `更新状态失败`);
  }
};

const userRole = computed(() => authStore.userRole);
const isCS = computed(() => userRole.value === UserRole.CUSTOMER_SERVICE);
const isTech = computed(() => userRole.value === UserRole.DEVELOPER);
const isFinance = computed(() => userRole.value === UserRole.FINANCE);

const canCancelOrder = computed(() => {
  if (!order.value || !(isCS.value || userRole.value === UserRole.SUPER_ADMIN)) return false;
  return ![OrderStatus.SETTLED, OrderStatus.CANCELLED].includes(order.value.status);
});

const canRevertToDev = computed(() => {
  if (!order.value || !isCS.value) return false;
  return [OrderStatus.SHIPPED, OrderStatus.RECEIVED].includes(order.value.status);
});

const isTechAndCanSettle = computed(
  () => isTech.value && order.value?.status === OrderStatus.RECEIVED
);

const isAssignedDeveloper = computed(() => {
  const currentUserId = authStore.user?.sub ? parseInt(authStore.user.sub, 10) : null;
  return order.value?.developer?.id === currentUserId;
});

const handleLogSubmit = async (values: { log_content: string }) => {
  if (!order.value) return;

  isLogSubmitting.value = true;
  try {
    // 直接使用 values.log_content
    await orderService.addWorkLog(order.value.id, { log_content: values.log_content });
    message.success('工作日志提交成功');

    // 提交成功后，重置表单状态
    logFormState.log_content = '';

    await fetchOrder(); // 重新获取订单数据以显示新日志
  } catch (error: any) {
    message.error(error.response?.data?.msg || '日志提交失败');
  } finally {
    isLogSubmitting.value = false;
  }
};

const showPriceModal = () => {
  newPrice.value = order.value?.final_price;
  isPriceModalOpen.value = true;
};

const showAssignTechModal = async () => {
  isAssignTechModalOpen.value = true;
  devsLoading.value = true;
  try {
    developers.value = await userService.getAvailableDevelopers();
    // 【FIX 2】使用正确的属性访问方式
    selectedTechId.value = order.value?.developer?.id;
  } catch (error) {
    message.error('获取技术人员列表失败');
  } finally {
    devsLoading.value = false;
  }
};

const handleUpdatePrice = async () => {
  if (!order.value || newPrice.value === undefined) {
    message.warn('请输入有效的价格');
    return;
  }
  try {
    await orderService.updateOrderDetails(order.value.id, { final_price: newPrice.value });
    message.success('价格更新成功');
    isPriceModalOpen.value = false;
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || '价格更新失败');
  }
};

const handleAssignTech = async () => {
  if (!order.value || selectedTechId.value === undefined) {
    message.warn('请选择一位技术人员');
    return;
  }
  try {
    await orderService.updateOrderDetails(order.value.id, {
      developer_id: selectedTechId.value,
    });
    message.success('技术负责人已更新');
    isAssignTechModalOpen.value = false;
    await fetchOrder();
  } catch (error: any) {
    message.error(error.response?.data?.msg || '分配失败');
  }
};

const getStatusColor = (status: OrderStatus) => {
  const colorMap: Record<OrderStatus, string> = {
    [OrderStatus.PENDING_ASSIGNMENT]: 'orange',
    [OrderStatus.PENDING_PAYMENT]: 'gold',
    [OrderStatus.IN_DEVELOPMENT]: 'processing',
    [OrderStatus.SHIPPED]: 'blue',
    [OrderStatus.RECEIVED]: 'cyan',
    [OrderStatus.PENDING_SETTLEMENT]: 'purple',
    [OrderStatus.VERIFIED]: 'lime',
    [OrderStatus.SETTLED]: 'success',
    [OrderStatus.CANCELLED]: 'default',
  };
  return colorMap[status] || 'default';
};
</script>

<style scoped>
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
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 992px) {
  /* 在中等屏幕下变为单栏布局 */
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
