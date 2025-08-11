# backend/app/services/user_service.py

import bcrypt
from .. import db
from ..models.user import User, UserRole
from ..schemas import user_schemas
import openpyxl
from io import BytesIO

# +--- 新增的完整函数开始 ---+
def batch_import_users(file_stream: BytesIO) -> dict:
    """
    从Excel文件流中批量导入用户。
    Excel文件应包含表头: username, password, full_name, role, gender, 
                        skills (多个用逗号分隔), default_commission_rate, financial_account
    其中 username, password, full_name, role 是必需的。
    
    :param file_stream: 文件IO流
    :return: 一个包含成功和失败信息的字典
    """
    try:
        workbook = openpyxl.load_workbook(file_stream)
        sheet = workbook.active
    except Exception as e:
        raise ValueError(f"无法读取或解析Excel文件: {e}")

    header = [cell.value for cell in sheet[1]]
    required_headers = ['username', 'password', 'full_name', 'role']
    if not all(h in header for h in required_headers):
        raise ValueError(f"Excel文件表头必须至少包含: {', '.join(required_headers)}")

    results = {"success_count": 0, "failure_count": 0, "errors": []}
    
    # 从第二行开始读取数据
    for row_index in range(2, sheet.max_row + 1):
        # 将行数据与表头打包成字典
        row_data = dict(zip(header, [cell.value for cell in sheet[row_index]]))
        username = row_data.get('username')

        # 跳过没有用户名的行
        if not username:
            results["failure_count"] += 1
            results["errors"].append(f"第 {row_index} 行: 'username' 不能为空。")
            continue

        try:
            # 使用Pydantic Schema进行数据校验和转换
            user_data_dict = {
                "username": username,
                "password": str(row_data.get('password')) if row_data.get('password') else '123456', # 默认密码
                "full_name": row_data.get('full_name'),
                "role": UserRole(row_data.get('role')), # 会自动校验角色枚举值是否有效
                "gender": row_data.get('gender'),
                "skills": row_data.get('skills').split(',') if row_data.get('skills') and isinstance(row_data.get('skills'), str) else None,
                "default_commission_rate": row_data.get('default_commission_rate'),
                "financial_account": row_data.get('financial_account')
            }
            # 清理None值，以便Pydantic使用默认值
            user_data_dict_cleaned = {k: v for k, v in user_data_dict.items() if v is not None}
            
            user_create_schema = user_schemas.UserCreate(**user_data_dict_cleaned)
            
            # 调用已有的创建用户服务，它内部包含了对用户名是否存在的检查
            # 注意：这里我们为每个用户开启一个子事务，以处理单行错误而不影响整个批处理
            try:
                db.session.begin_nested()
                create_user(user_create_schema)
                db.session.commit() # 提交子事务
                results["success_count"] += 1
            except Exception as e_inner:
                db.session.rollback() # 回滚子事务
                raise e_inner # 重新抛出错误，由外层捕获

        except ValueError as e: # 捕获用户名已存在等业务错误
             results["failure_count"] += 1
             results["errors"].append(f"第 {row_index} 行 (用户: {username}): {e}")
        except Exception as e: # 捕获其他所有错误，如角色名称无效
            results["failure_count"] += 1
            results["errors"].append(f"第 {row_index} 行 (用户: {username}): 导入失败 - {e}")
            
    return results

def get_user_by_username(username: str) -> User | None:
    return User.query.filter_by(username=username).first()

def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)

def get_all_users() -> list[User]:
    return User.query.order_by(User.id).all()

def get_active_developers() -> list[User]:
    """获取所有已启用的技术人员列表"""
    return User.query.filter_by(role=UserRole.DEVELOPER, is_active=True).order_by(User.id).all()

def create_user(user_data: user_schemas.UserCreate) -> User:
    """创建新用户"""
    if get_user_by_username(user_data.username):
        raise ValueError("Username already exists")

    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hashed_password.decode('utf-8'),
        role=user_data.role,
        gender=user_data.gender,
        skills=user_data.skills,
        default_commission_rate=user_data.default_commission_rate,
        financial_account=user_data.financial_account
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_user(user_id: int, update_data: user_schemas.UserUpdate) -> User:
    """更新用户信息"""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    if 'username' in update_dict and update_dict['username'] != user.username:
        if get_user_by_username(update_dict['username']):
            raise ValueError("Username already exists")

    for key, value in update_dict.items():
        if key == 'password':
            if value: # 确保密码非空
                hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                setattr(user, 'password_hash', hashed_password.decode('utf-8'))
        else:
            setattr(user, key, value)
            
    db.session.commit()
    return user

def toggle_user_status(user_id: int) -> User:
    """启用/禁用用户"""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
    
    user.is_active = not user.is_active
    db.session.commit()
    return user

def delete_user(user_id: int):
    """删除用户"""
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    db.session.delete(user)
    db.session.commit()