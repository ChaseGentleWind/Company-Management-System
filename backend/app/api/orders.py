# backend/app/api/orders.py

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from .. import db
from ..models.user import UserRole
# --- 修改 schemas 导入 ---
from ..schemas import order_schemas, work_log_schemas
from ..utils.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# --- 修改 services 导入 ---
from ..services import order_service, work_log_service

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(UserRole.CUSTOMER_SERVICE.value)
def create_order():
    """客服创建新订单"""
    try:
        order_data = order_schemas.OrderCreate.model_validate(request.get_json())
        current_user_id = int(get_jwt_identity())

        # --- CHANGED: 调用服务层来处理业务逻辑 ---
        new_order = order_service.create_order(order_data, current_user_id)
        
        db.session.refresh(new_order) # 刷新以加载关系
        return jsonify(order_schemas.OrderOut.model_validate(new_order).model_dump(mode='json')), 201

    except ValidationError as e:
        return jsonify(e.errors()), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """获取订单列表（根据角色区分）"""
    claims = get_jwt()
    user_role = claims.get("role")
    user_id = int(get_jwt_identity())
    
    # --- CHANGED: 调用服务层来获取数据 ---
    orders = order_service.get_orders_for_user(user_id, user_role)

    orders_out = [order_schemas.OrderOut.model_validate(order).model_dump(mode='json') for order in orders]
    return jsonify(orders_out), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id: int):
    """获取单个订单的详细信息"""
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({"msg": "Order not found"}), 404
    
    # 此处可以加入权限校验，确保只有相关人员能查看
    
    return jsonify(order_schemas.OrderOut.model_validate(order).model_dump(mode='json')), 200


@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@jwt_required()
def update_order_status_route(order_id: int):
    """
    核心接口：驱动订单生命周期流转
    """
    try:
        claims = get_jwt()
        user_role = claims.get("role")
        
        order = order_service.get_order_by_id(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404

        data = order_schemas.OrderStatusUpdate.model_validate(request.get_json())
        
        # 调用服务层处理状态变更
        order_service.update_order_status(order, data.status, user_role)

        return jsonify({"message": f"订单状态已成功更新为 [{data.status.value}]"}), 200

    except ValidationError as e:
        return jsonify(e.errors()), 400
    except (ValueError, PermissionError) as e:
        return jsonify({"msg": str(e)}), 400 # 400 Bad Request for invalid transition
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500


@orders_bp.route('/<int:order_id>', methods=['PATCH'])
@jwt_required()
@role_required(UserRole.CUSTOMER_SERVICE.value)
def update_order_details_route(order_id: int):
    """客服更新订单信息，如价格、分配技术"""
    try:
        order = order_service.get_order_by_id(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404
        
        update_data = order_schemas.OrderUpdateByCs.model_validate(request.get_json())
        
        # 调用服务层处理更新
        updated_order = order_service.update_order_details_by_cs(order, update_data)
        
        return jsonify(order_schemas.OrderOut.model_validate(updated_order).model_dump(mode='json')), 200

    except ValidationError as e:
        return jsonify(e.errors()), 400
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500


@orders_bp.route('/<int:order_id>/commission-override', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN.value)
def set_commission_override_route(order_id: int):
    """超管为特定订单设置特殊提成比例"""
    try:
        order = order_service.get_order_by_id(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404
            
        override_data = order_schemas.CommissionOverrideUpdate.model_validate(request.get_json())

        order_service.set_commission_override(order, override_data)
        
        return '', 204 # 204 No Content表示成功，无需返回内容
        
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500
    
    # ---【任务 4.1】新增工作日志提交 API ---
@orders_bp.route('/<int:order_id>/work_logs', methods=['POST'])
@jwt_required()
@role_required(UserRole.DEVELOPER.value)
def add_work_log_route(order_id: int):
    """技术人员为指定订单提交工作日志"""
    try:
        order = order_service.get_order_by_id(order_id)
        if not order:
            return jsonify({"msg": "Order not found"}), 404

        current_user_id = int(get_jwt_identity())
        claims = get_jwt()
        user_role = claims.get("role")

        log_data = work_log_schemas.WorkLogCreate.model_validate(request.get_json())
        
        # 调用服务层处理业务逻辑
        new_log = work_log_service.add_work_log(order, current_user_id, user_role, log_data)
        
        # 刷新以加载关系
        db.session.refresh(new_log)
        return jsonify(work_log_schemas.WorkLogOut.model_validate(new_log).model_dump(mode='json')), 201

    except ValidationError as e:
        return jsonify(e.errors()), 400
    except (ValueError, PermissionError) as e:
        return jsonify({"msg": str(e)}), 403 # 403 Forbidden for permission issues
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500