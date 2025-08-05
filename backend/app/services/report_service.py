# backend/app/services/report_service.py

from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from .. import db
from ..models.order import Order, OrderStatus
from ..models.commission import Commission
from ..models.user import UserRole

def generate_settled_orders_report(start_date_str: str, end_date_str: str) -> BytesIO:
    """
    根据时间范围生成已结算订单的Excel报表。
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        # 结束日期需要包含当天，所以设置为当天的23:59:59
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except (ValueError, TypeError):
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    # 1. 查询已结算的订单
    orders = db.session.query(Order).filter(
        Order.status == OrderStatus.SETTLED,
        Order.updated_at.between(start_date, end_date)
    ).order_by(Order.updated_at.desc()).all()

    # 2. 创建Excel工作簿
    workbook = Workbook()
    ws = workbook.active
    ws.title = "已结算订单报表"

    # 3. 设置表头
    headers = [
        "订单业务ID", "结算时间", "客户姓名", "订单金额", 
        "客服", "客服提成", "技术", "技术提成"
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # 4. 填充数据
    for order in orders:
        # 获取关联的提成记录
        commissions = {
            comm.role_at_time: comm.amount 
            for comm in order.commissions
        }
        
        cs_commission = commissions.get(UserRole.CUSTOMER_SERVICE.value, 0)
        dev_commission = commissions.get(UserRole.DEVELOPER.value, 0)

        row_data = [
            order.order_uid,
            order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.customer_info.get('name', 'N/A'),
            order.final_price,
            order.creator.full_name if order.creator else 'N/A',
            cs_commission,
            order.developer.full_name if order.developer else 'N/A',
            dev_commission
        ]
        ws.append(row_data)

    # 调整列宽 (可选，但能提升可读性)
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # 获取列的字母
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 5. 将工作簿保存到内存中
    excel_file = BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)
    
    return excel_file