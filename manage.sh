#!/bin/bash

# 快速启动脚本 - 用于日常管理
# 版本: 1.0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_help() {
    echo "企业管理系统 - 快速管理脚本"
    echo ""
    echo "用法: ./manage.sh [命令]"
    echo ""
    echo "可用命令:"
    echo "  start       启动所有服务"
    echo "  stop        停止所有服务"  
    echo "  restart     重启所有服务"
    echo "  status      查看服务状态"
    echo "  logs        查看日志"
    echo "  health      健康检查"
    echo "  backup      备份数据库"
    echo "  update      更新服务"
    echo "  clean       清理Docker资源"
    echo "  help        显示帮助信息"
}

case "$1" in
    start)
        echo -e "${GREEN}启动服务...${NC}"
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    stop)
        echo -e "${YELLOW}停止服务...${NC}"
        docker-compose -f docker-compose.prod.yml down
        ;;
    restart)
        echo -e "${YELLOW}重启服务...${NC}"
        docker-compose -f docker-compose.prod.yml restart
        ;;
    status)
        echo -e "${GREEN}服务状态:${NC}"
        docker-compose -f docker-compose.prod.yml ps
        ;;
    logs)
        docker-compose -f docker-compose.prod.yml logs -f ${2:-}
        ;;
    health)
        ./health-check.sh
        ;;
    backup)
        echo -e "${GREEN}备份数据库...${NC}"
        backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f docker-compose.prod.yml exec -T db mysqldump -u root -p$MYSQL_ROOT_PASSWORD $MYSQL_DATABASE > "backups/$backup_file"
        echo "备份完成: backups/$backup_file"
        ;;
    update)
        echo -e "${GREEN}更新服务...${NC}"
        docker-compose -f docker-compose.prod.yml pull
        docker-compose -f docker-compose.prod.yml up -d --build
        ;;
    clean)
        echo -e "${YELLOW}清理Docker资源...${NC}"
        docker system prune -f
        ;;
    help|*)
        show_help
        ;;
esac