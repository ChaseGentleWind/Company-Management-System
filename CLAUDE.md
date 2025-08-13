# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

这是一个前后端分离的企业管理系统，用于管理客户订单、开发任务分配、财务结算等业务流程。

## 技术架构

### 前端 (frontend/)
- **框架**: Vue 3 + TypeScript + Vite
- **UI库**: Ant Design Vue 4.x
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts + vue-echarts
- **开发端口**: 8080

### 后端 (backend/)
- **框架**: Flask 2.3.2
- **ORM**: SQLAlchemy 3.0.5 + Flask-Migrate
- **数据库**: MySQL 8.0
- **认证**: Flask-JWT-Extended (JWT Token)
- **数据验证**: Pydantic 2.x
- **密码加密**: bcrypt
- **服务端口**: 5000

## 常用开发命令

### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (localhost:8080)
npm run dev

# 构建生产版本
npm run build

# 类型检查
npm run type-check

# 代码检查和修复
npm run lint

# 代码格式化
npm run format
```

### 后端开发
```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器 (localhost:5000)
python manage.py

# 数据库迁移
flask db upgrade

# 创建超级管理员用户
python manage.py create-admin <username> <password>
```

## 项目结构与架构

### 前端架构
- **入口**: `frontend/src/main.ts` - 应用初始化，注册Pinia、Router、Ant Design Vue
- **路由**: `frontend/src/router/index.ts` - 路由配置，包含权限守卫和角色控制
- **布局**: `frontend/src/layouts/MainLayout.vue` - 主布局组件，侧边栏+顶部导航
- **状态管理**: `frontend/src/stores/` - Pinia stores，包含auth、notifications等
- **API服务**: `frontend/src/services/` - HTTP请求封装，包含拦截器处理
- **类型定义**: `frontend/src/services/types.ts` - TypeScript类型定义

**关键组件目录结构**:
- `components/admin/` - 用户管理相关组件
- `components/orders/` - 订单管理相关组件
- `views/` - 页面组件
- `composables/` - Vue组合式函数

### 后端架构
**分层架构**: Controller (API) → Service → Model → Database

- **应用工厂**: `backend/app/__init__.py` - Flask应用创建，插件初始化
- **配置**: `backend/config.py` - 数据库连接、JWT配置等
- **API层**: `backend/app/api/` - RESTful API端点
- **服务层**: `backend/app/services/` - 业务逻辑处理
- **模型层**: `backend/app/models/` - SQLAlchemy数据模型
- **数据验证**: `backend/app/schemas/` - Pydantic schemas
- **工具类**: `backend/app/utils/decorators.py` - 权限装饰器等

**API路由前缀**:
- `/api/auth` - 认证相关
- `/api/users` - 用户管理
- `/api/orders` - 订单管理
- `/api/notifications` - 通知系统
- `/api/v1/dashboard` - 仪表盘
- `/api/v1/reports` - 报表

### 数据库模型关系
- **User** - 用户表，支持多角色(SUPER_ADMIN, CUSTOMER_SERVICE, DEVELOPER, FINANCE)
- **Order** - 订单表，关联创建者和开发者
- **WorkLog** - 工作日志表，记录开发进度
- **Commission** - 提成记录表
- **Notification** - 通知表

### 权限系统
- **JWT Token认证**: 30天有效期
- **角色权限控制**: 前端路由守卫 + 后端装饰器
- **角色说明**:
  - SUPER_ADMIN: 系统管理员，全部权限
  - CUSTOMER_SERVICE: 客服，创建订单、分配开发者
  - DEVELOPER: 开发者，查看分配订单、提交工作日志
  - FINANCE: 财务，查看报表、处理结算

## 开发注意事项

### 环境配置
- 需要`.env`文件配置数据库连接信息和密钥
- MySQL数据库需要预先创建
- 前端代理配置指向localhost:5000

### API调用约定
- 所有API请求需要Bearer Token认证(除登录接口)
- 请求头统一使用`application/json`
- 401错误会自动跳转到登录页面

### 状态管理
- 使用Pinia进行状态管理
- 用户信息和Token存储在localStorage
- 通知状态实时更新

### 数据库迁移
使用Flask-Migrate管理数据库版本:
```bash
# 创建新迁移
flask db migrate -m "描述"

# 应用迁移
flask db upgrade

# 查看迁移历史
flask db history
```

### Docker部署
项目包含Dockerfile和docker-compose.yml.bak配置文件，支持容器化部署。前端使用Nginx serve静态文件，后端使用Gunicorn运行。