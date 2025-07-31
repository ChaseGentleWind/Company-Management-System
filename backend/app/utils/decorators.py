from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(required_role: str):
    """
    一个装饰器，用于验证用户是否具有特定角色。
    :param required_role: 所需的角色名 (例如 'SUPER_ADMIN')
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

            # 检查角色是否匹配
            if user_role != required_role:
                return jsonify({"msg": "Forbidden: Insufficient permissions"}), 403
            
            # 角色匹配，执行原函数
            return fn(*args, **kwargs)
        return wrapper
    return decorator