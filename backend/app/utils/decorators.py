from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from typing import Union, List  # 导入 Union 和 List 用于类型提示

def role_required(required_roles: Union[str, List[str]]):
    """
    一个装饰器，用于验证用户是否具有所需的角色。
    它既可以接收单个角色字符串，也可以接收一个包含多个可接受角色的列表。
    
    :param required_roles: 所需的角色名，或一个包含多个角色名的列表。
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 首先，验证JWT是否存在且有效
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({"msg": f"JWT verification failed: {str(e)}"}), 401

            # 获取JWT中的声明
            claims = get_jwt()
            # 从 additional_claims 中获取角色
            user_role = claims.get("role", None)

            # 如果Token中没有角色信息，则拒绝访问
            if user_role is None:
                return jsonify({"msg": "Forbidden: Role information missing in token"}), 403

            # --- 核心修复逻辑 ---
            is_authorized = False
            if isinstance(required_roles, str):
                # 情况一：要求的是单个角色（字符串）
                if user_role == required_roles:
                    is_authorized = True
            elif isinstance(required_roles, list):
                # 情况二：要求的是角色列表中的任意一个
                if user_role in required_roles:
                    is_authorized = True

            # 如果用户角色不符合要求，则返回 403 禁止访问
            if not is_authorized:
                return jsonify({"msg": "Forbidden: Insufficient permissions"}), 403
            
            # 角色匹配，执行原函数
            return fn(*args, **kwargs)
        return wrapper
    return decorator