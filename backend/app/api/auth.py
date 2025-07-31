from flask import Blueprint, request, jsonify
from ..models.user import User
from flask_jwt_extended import create_access_token
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    # 简化: 显式地检查用户存在并且密码匹配
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        if not user.is_active:
            return jsonify({"msg": "User account is disabled"}), 403

        # 创建Token时可以附带一些非敏感信息
        additional_claims = {"role": user.role.value, "full_name": user.full_name}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad username or password"}), 401