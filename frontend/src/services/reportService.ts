// frontend/src/services/reportService.ts

import apiClient from './api'

// 一个帮助函数，用于处理从API返回的Blob数据并触发浏览器下载
function downloadFile(blob: Blob, filename: string) {
  // 创建一个指向Blob的URL
  const url = window.URL.createObjectURL(blob);
  // 创建一个隐藏的<a>标签
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  // 将<a>标签添加到页面，模拟点击，然后移除
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  // 释放URL对象
  window.URL.revokeObjectURL(url);
}

export const reportService = {
  /**
   * 下载已结算订单的Excel报表
   * @param startDate 开始日期 'YYYY-MM-DD'
   * @param endDate 结束日期 'YYYY-MM-DD'
   */
  async downloadSettledOrdersReport(startDate: string, endDate: string): Promise<void> {
    const response = await apiClient.get('/v1/reports/settled-orders', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
      responseType: 'blob' // 告诉axios期望接收一个Blob类型的数据
    });

    // 从响应头中获取文件名
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'report.xlsx'; // 默认文件名
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch && filenameMatch.length > 1) {
        filename = filenameMatch[1];
      }
    }

    downloadFile(response.data, filename);
  }
}
