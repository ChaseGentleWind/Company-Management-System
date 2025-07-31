# backend/app/api/orders.py

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from .. import db
from ..models.user import User, UserRole
from ..models.order import Order
from ..schemas import order_schemas
from ..utils.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(UserRole.CUSTOMER_SERVICE.value)
def create_order():
    """客服创建新订单"""
    try:
        # --- 这部分逻辑保持不变 ---
        order_data = order_schemas.OrderCreate.model_validate(request.get_json())
        current_user_id = int(get_jwt_identity())

        if order_data.developer_id:
            developer = db.session.get(User, order_data.developer_id)
            if not developer or developer.role != UserRole.DEVELOPER:
                return jsonify({"msg": "Invalid developer ID"}), 400

        new_order = Order(
            creator_id=current_user_id,
            **order_data.model_dump()
        )

        db.session.add(new_order)
        db.session.commit()
        
        # 刷新对象以加载关系
        db.session.refresh(new_order)

        return jsonify(order_schemas.OrderOut.model_validate(new_order).model_dump(mode='json')), 201

    except ValidationError as e:
        # --- 修改这里的错误处理 ---
        # e.errors() 返回的是一个列表，我们直接将其 jsonify
        return jsonify(e.errors()), 400
    except Exception as e:
        db.session.rollback()
        # 确保返回的错误信息是可序列化的字符串
        return jsonify({"msg": "An unexpected error occurred", "details": str(e)}), 500


@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """获取订单列表（根据角色区分）"""
    claims = get_jwt()
    user_role = claims.get("role")
    user_id = int(get_jwt_identity())
    
    query = Order.query.order_by(Order.created_at.desc())

    # 不同角色看到不同的订单列表
    if user_role == UserRole.SUPER_ADMIN.value or user_role == UserRole.FINANCE.value:
        # 超管和财务能看所有订单
        orders = query.all()
    elif user_role == UserRole.CUSTOMER_SERVICE.value:
        # 客服只能看自己创建的订单
        orders = query.filter_by(creator_id=user_id).all()
    elif user_role == UserRole.DEVELOPER.value:
        # 技术只能看分配给自己的订单
        orders = query.filter_by(developer_id=user_id).all()
    else:
        # 其他未知角色或无角色，返回空列表
        return jsonify([]), 200

    orders_out = [order_schemas.OrderOut.model_validate(order).model_dump(mode='json') for order in orders]
    return jsonify(orders_out), 200