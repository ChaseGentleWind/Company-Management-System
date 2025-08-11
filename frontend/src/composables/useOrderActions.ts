import { computed, type Ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { type Order, OrderStatus, UserRole } from '@/services/types'

/**
 * 封装订单详情页中的所有操作逻辑和权限判断
 * @param order - 一个包含订单信息的 Ref 对象
 */
export function useOrderActions(order: Ref<Order | null>) {
  const authStore = useAuthStore()
  const userRole = computed(() => authStore.userRole)
  const currentUserId = computed(() => (authStore.user?.sub ? parseInt(authStore.user.sub, 10) : null))

  // --- 角色判断 ---
  const isCS = computed(() => userRole.value === UserRole.CUSTOMER_SERVICE)
  const isTech = computed(() => userRole.value === UserRole.DEVELOPER)
  const isFinance = computed(() => userRole.value === UserRole.FINANCE)
  const isSuperAdmin = computed(() => userRole.value === UserRole.SUPER_ADMIN)
  const isAssignedDeveloper = computed(() => order.value?.developer?.id === currentUserId.value)

  // + 新增：判断是否可以设置特殊提成
  const canSetSpecialCommission = computed(() => {
    return isSuperAdmin.value && !!order.value;
  });

  // --- 权限计算属性 ---
  const canCancelOrder = computed(() => {
    if (!order.value) return false;
    // + 如果是超管，则忽略锁定状态
    if (isSuperAdmin.value) return ![OrderStatus.SETTLED, OrderStatus.CANCELLED].includes(order.value.status);
    // 对其他角色，保持原有逻辑
    if (!isCS.value) return false;
    return !order.value.is_locked && ![OrderStatus.SETTLED, OrderStatus.CANCELLED].includes(order.value.status);
  });

  const canRevertToDev = computed(() => {
    if (!order.value) return false;
    // + 如果是超管，则忽略锁定状态
    if (isSuperAdmin.value) return [OrderStatus.SHIPPED, OrderStatus.RECEIVED].includes(order.value.status);
    // 对其他角色，保持原有逻辑
    if (!isCS.value) return false;
    return !order.value.is_locked && [OrderStatus.SHIPPED, OrderStatus.RECEIVED].includes(order.value.status);
  });


  const canSettleByTech = computed(() => {
    return isTech.value && isAssignedDeveloper.value && order.value?.status === OrderStatus.RECEIVED
  })

  const canAddWorkLog = computed(() => {
      return isAssignedDeveloper.value && !order.value?.is_locked
  })

  // --- 返回所有r计算属性和方法 ---
  return {
    // 角色
    isCS,
    isTech,
    isFinance,
    isSuperAdmin,
    isAssignedDeveloper,

    // 权限
    canCancelOrder,
    canRevertToDev,
    canSettleByTech,
    canAddWorkLog,
    canSetSpecialCommission,
  }
}
