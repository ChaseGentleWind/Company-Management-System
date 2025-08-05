# backend/app/api/reports.py

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from ..services import report_service
from ..models.user import UserRole
from ..utils.decorators import role_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/settled-orders', methods=['GET'])
@jwt_required()
@role_required([UserRole.FINANCE.value, UserRole.SUPER_ADMIN.value]) # 假设只有财务可以导出
def download_settled_orders_report():
    """
    下载已结算订单的Excel报表.
    接收查询参数: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({"msg": "start_date and end_date query parameters are required."}), 400

    try:
        excel_file = report_service.generate_settled_orders_report(start_date, end_date)
        
        filename = f"settled_orders_{start_date}_to_{end_date}.xlsx"
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        # 在生产环境中，应该记录更详细的错误日志
        return jsonify({"msg": "An unexpected error occurred while generating the report."}), 500