<template>
  <div>
    <a-page-header title="财务报表" sub-title="下载已结算的订单报表" />
    <div class="content-card">
      <a-card>
        <a-space direction="vertical" :size="24">
          <p>请选择需要导出报表的时间范围，系统将生成该时间段内所有“已结算”订单的 Excel 文件。</p>
          <a-range-picker v-model:value="dateRange" size="large" />
          <a-button 
            type="primary" 
            :loading="downloading" 
            :disabled="!dateRange" 
            @click="handleDownload"
            size="large"
          >
            <template #icon><DownloadOutlined /></template>
            下载报表
          </a-button>
        </a-space>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  PageHeader as APageHeader,
  Card as ACard,
  RangePicker as ARangePicker,
  Button as AButton,
  Space as ASpace,
  message,
} from 'ant-design-vue';
import { DownloadOutlined } from '@ant-design/icons-vue';
import { reportService } from '@/services/reportService';
import type { Dayjs } from 'dayjs';

const dateRange = ref<[Dayjs, Dayjs]>();
const downloading = ref(false);

const handleDownload = async () => {
  if (!dateRange.value) {
    message.warning('请选择一个日期范围');
    return;
  }
  
  downloading.value = true;
  try {
    const startDate = dateRange.value[0].format('YYYY-MM-DD');
    const endDate = dateRange.value[1].format('YYYY-MM-DD');
    await reportService.downloadSettledOrdersReport(startDate, endDate);
    message.success('报表已开始下载！');
  } catch (error: any) {
    console.error("Download failed:", error);
    message.error(error.response?.data?.msg || '报表下载失败，请稍后重试。');
  } finally {
    downloading.value = false;
  }
};
</script>

<style scoped>
.content-card {
  margin: 0 24px;
}
</style>