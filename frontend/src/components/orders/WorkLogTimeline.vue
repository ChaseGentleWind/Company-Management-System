<template>
  <a-card title="工作日志">
    <a-timeline v-if="logs.length > 0">
      <a-timeline-item v-for="log in logs" :key="log.id">
        <p><strong>{{ log.developer.full_name }}</strong></p>
        <p>{{ log.log_content }}</p>
        <p style="color: #888; font-size: 12px">{{ new Date(log.created_at).toLocaleString() }}</p>
      </a-timeline-item>
    </a-timeline>
    <a-empty v-else description="暂无工作日志" />
  </a-card>
</template>

<script setup lang="ts">
import type { PropType } from 'vue'
import type { WorkLog } from '@/services/types'
import { Card as ACard, Timeline as ATimeline, TimelineItem as ATimelineItem, Empty as AEmpty } from 'ant-design-vue'

defineProps({
  logs: {
    type: Array as PropType<WorkLog[]>,
    required: true
  }
})
</script>
