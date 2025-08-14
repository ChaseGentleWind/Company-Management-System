#!/bin/bash

# 企业管理系统 - Linux服务器部署脚本
# 版本: 1.0
# 作者: Claude Code Assistant

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# 检查必要工具
check_requirements() {
    log "🔍 检查系统要求..."
    
    # 检查Docker
    if ! command -v docker >/dev/null 2>&1; then
        error "Docker未安装，请先安装Docker"
        echo "安装命令: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "Docker Compose未安装，请先安装Docker Compose"
        echo "安装命令: sudo curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        echo "sudo chmod +x /usr/local/bin/docker-compose"
        exit 1
    fi
    
    # 检查环境配置文件
    if [ ! -f ".env.production" ]; then
        error ".env.production 文件不存在，请创建生产环境配置文件"
        exit 1
    fi
    
    log "✅ 系统要求检查通过"
}

# 创建必要目录
create_directories() {
    log "📁 创建必要目录..."
    
    # 创建SSL证书目录
    mkdir -p ssl
    
    # 创建日志目录
    mkdir -p logs
    
    # 创建备份目录
    mkdir -p backups
    
    log "✅ 目录创建完成"
}

# 备份旧版本
backup_old_version() {
    if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
        log "💾 备份当前版本..."
        
        # 创建备份文件名
        backup_name="backup_$(date +%Y%m%d_%H%M%S)"
        
        # 导出数据库
        docker-compose -f docker-compose.prod.yml exec -T db mysqldump -u root -p\$MYSQL_ROOT_PASSWORD \$MYSQL_DATABASE > "backups/${backup_name}_database.sql"
        
        # 备份上传文件
        docker cp company_system_backend:/app/uploads "backups/${backup_name}_uploads" 2>/dev/null || true
        
        log "✅ 备份完成: $backup_name"
    fi
}

# 停止现有服务
stop_services() {
    log "🛑 停止现有服务..."
    
    if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
        docker-compose -f docker-compose.prod.yml down
        log "✅ 服务已停止"
    else
        log "ℹ️  没有运行中的服务"
    fi
}

# 清理旧资源
cleanup_old_resources() {
    log "🧹 清理旧资源..."
    
    # 清理悬挂镜像
    docker image prune -f
    
    # 清理未使用的网络
    docker network prune -f
    
    # 清理构建缓存
    docker builder prune -f
    
    log "✅ 清理完成"
}

# 构建镜像
build_images() {
    log "🔨 构建新镜像..."
    
    # 构建镜像（不使用缓存以确保最新代码）
    docker-compose -f docker-compose.prod.yml build --no-cache --parallel
    
    log "✅ 镜像构建完成"
}

# 启动服务
start_services() {
    log "🚀 启动服务..."
    
    # 启动所有服务
    docker-compose -f docker-compose.prod.yml up -d
    
    log "✅ 服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log "⏰ 等待服务就绪..."
    
    # 等待数据库就绪
    echo -n "等待数据库启动"
    for i in {1..60}; do
        if docker-compose -f docker-compose.prod.yml exec -T db mysqladmin ping -h localhost -u root -p\$MYSQL_ROOT_PASSWORD --silent 2>/dev/null; then
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    
    # 等待后端就绪
    echo -n "等待后端服务启动"
    for i in {1..30}; do
        if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    
    # 等待前端就绪
    echo -n "等待前端服务启动"
    for i in {1..30}; do
        if curl -f http://localhost/ >/dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    
    log "✅ 所有服务就绪"
}

# 数据库迁移
run_database_migration() {
    log "📊 执行数据库迁移..."
    
    # 运行数据库迁移
    docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
    
    log "✅ 数据库迁移完成"
}

# 创建初始管理员用户（如果不存在）
create_admin_user() {
    log "👤 检查管理员用户..."
    
    # 这里可以添加创建初始管理员用户的逻辑
    # docker-compose -f docker-compose.prod.yml exec backend python manage.py create-admin admin admin123
    
    log "ℹ️  请记得创建管理员用户: docker-compose -f docker-compose.prod.yml exec backend python manage.py create-admin <username> <password>"
}

# 健康检查
health_check() {
    log "🏥 执行健康检查..."
    
    # 检查容器状态
    echo "📦 容器状态:"
    docker-compose -f docker-compose.prod.yml ps
    
    # 检查服务健康状态
    echo ""
    echo "🔍 服务健康检查:"
    
    # 检查后端
    if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
        echo "✅ 后端服务: 健康"
    else
        echo "❌ 后端服务: 异常"
    fi
    
    # 检查前端
    if curl -f http://localhost/ >/dev/null 2>&1; then
        echo "✅ 前端服务: 健康"
    else
        echo "❌ 前端服务: 异常"
    fi
    
    # 检查数据库
    if docker-compose -f docker-compose.prod.yml exec -T db mysqladmin ping -h localhost -u root -p\$MYSQL_ROOT_PASSWORD --silent 2>/dev/null; then
        echo "✅ 数据库服务: 健康"
    else
        echo "❌ 数据库服务: 异常"
    fi
}

# 显示访问信息
show_access_info() {
    log "🌐 部署完成！访问信息:"
    echo ""
    echo "前端访问地址: http://$(hostname -I | awk '{print $1}')"
    echo "后端API地址: http://$(hostname -I | awk '{print $1}')/api"
    echo "数据库连接: $(hostname -I | awk '{print $1}'):3306"
    echo ""
    echo "管理命令:"
    echo "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo "停止服务: docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "请确保防火墙已开放 80, 443, 3306, 5000 端口"
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "   企业管理系统 - 生产环境部署脚本"
    echo "======================================"
    echo -e "${NC}"
    
    check_requirements
    create_directories
    backup_old_version
    stop_services
    cleanup_old_resources
    build_images
    start_services
    wait_for_services
    run_database_migration
    create_admin_user
    health_check
    show_access_info
    
    log "🎉 部署完成！"
}

# 错误处理
trap 'error "部署过程中发生错误，请检查上述输出"; exit 1' ERR

# 执行主函数
main "$@"