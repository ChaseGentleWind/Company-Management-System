#!/bin/bash

# 企业管理系统 - 健康检查脚本
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

# 检查Docker服务
check_docker_services() {
    log "🐳 检查Docker服务状态..."
    
    if ! systemctl is-active --quiet docker; then
        error "Docker服务未运行"
        return 1
    else
        log "✅ Docker服务正常运行"
    fi
}

# 检查容器状态
check_containers() {
    log "📦 检查容器状态..."
    echo ""
    
    # 获取容器状态
    containers=$(docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}")
    echo "$containers"
    echo ""
    
    # 检查是否有异常容器
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Exit"; then
        warn "发现异常退出的容器"
        return 1
    else
        log "✅ 所有容器运行正常"
    fi
}

# 检查网络连接
check_network() {
    log "🌐 检查网络连接..."
    
    # 检查容器间网络
    if docker network ls | grep -q "company-management-system_app-network"; then
        log "✅ 应用网络存在"
    else
        error "应用网络不存在"
        return 1
    fi
}

# 检查数据库连接
check_database() {
    log "📊 检查数据库连接..."
    
    # 检查数据库是否可访问
    if docker-compose -f docker-compose.prod.yml exec -T db mysqladmin ping -h localhost --silent 2>/dev/null; then
        log "✅ 数据库连接正常"
        
        # 检查数据库表
        table_count=$(docker-compose -f docker-compose.prod.yml exec -T db mysql -e "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = '${MYSQL_DATABASE:-internal_system_db}';" --silent --skip-column-names 2>/dev/null | tail -1)
        log "数据库表数量: $table_count"
    else
        error "数据库连接失败"
        return 1
    fi
}

# 检查后端API
check_backend() {
    log "🔧 检查后端服务..."
    
    # 检查健康端点（需要先创建）
    if curl -f -s http://localhost:5000/api/auth/login >/dev/null 2>&1; then
        log "✅ 后端服务响应正常"
        
        # 检查API响应时间
        response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/api/auth/login 2>/dev/null || echo "timeout")
        if [ "$response_time" != "timeout" ]; then
            log "API响应时间: ${response_time}秒"
            
            # 警告响应时间过长
            if (( $(echo "$response_time > 2.0" | bc -l) )); then
                warn "API响应时间较长: ${response_time}秒"
            fi
        fi
    else
        error "后端服务无响应"
        return 1
    fi
}

# 检查前端服务
check_frontend() {
    log "🌐 检查前端服务..."
    
    # 检查前端页面
    if curl -f -s http://localhost/ >/dev/null 2>&1; then
        log "✅ 前端服务响应正常"
        
        # 检查前端资源加载
        if curl -f -s http://localhost/favicon.ico >/dev/null 2>&1; then
            log "静态资源加载正常"
        else
            warn "静态资源可能存在问题"
        fi
    else
        error "前端服务无响应"
        return 1
    fi
}

# 检查磁盘使用情况
check_disk_usage() {
    log "💾 检查磁盘使用情况..."
    
    # 检查根分区使用情况
    disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    log "根分区使用率: ${disk_usage}%"
    
    if [ "$disk_usage" -gt 90 ]; then
        error "磁盘使用率过高: ${disk_usage}%"
        return 1
    elif [ "$disk_usage" -gt 80 ]; then
        warn "磁盘使用率较高: ${disk_usage}%"
    fi
    
    # 检查Docker使用的磁盘空间
    docker_size=$(docker system df | awk 'NR==2 {print $3}')
    log "Docker使用空间: $docker_size"
}

# 检查内存使用情况
check_memory_usage() {
    log "🧠 检查内存使用情况..."
    
    # 检查系统内存使用
    memory_info=$(free -h | awk 'NR==2{printf "使用: %s, 可用: %s (%.2f%%)", $3,$7,$3*100/$2 }')
    log "系统内存: $memory_info"
    
    # 检查容器内存使用
    log "容器内存使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose -f docker-compose.prod.yml ps -q)
}

# 检查日志错误
check_logs() {
    log "📋 检查应用日志..."
    
    # 检查后端错误日志
    backend_errors=$(docker-compose -f docker-compose.prod.yml logs backend --tail=100 | grep -i "error\|exception\|fatal" | wc -l)
    if [ "$backend_errors" -gt 0 ]; then
        warn "后端日志中发现 $backend_errors 个错误"
        echo "最近错误："
        docker-compose -f docker-compose.prod.yml logs backend --tail=10 | grep -i "error\|exception\|fatal" | tail -5
    else
        log "✅ 后端日志无错误"
    fi
    
    # 检查前端错误日志
    frontend_errors=$(docker-compose -f docker-compose.prod.yml logs frontend --tail=100 | grep -i "error\|failed" | wc -l)
    if [ "$frontend_errors" -gt 0 ]; then
        warn "前端日志中发现 $frontend_errors 个错误"
    else
        log "✅ 前端日志无错误"
    fi
}

# 检查SSL证书（如果配置了HTTPS）
check_ssl() {
    if [ -d "ssl" ] && [ "$(ls -A ssl)" ]; then
        log "🔒 检查SSL证书..."
        
        # 检查证书过期时间
        for cert_file in ssl/*.crt ssl/*.pem; do
            if [ -f "$cert_file" ]; then
                exp_date=$(openssl x509 -in "$cert_file" -noout -dates | grep "notAfter" | cut -d= -f2)
                exp_timestamp=$(date -d "$exp_date" +%s)
                current_timestamp=$(date +%s)
                days_left=$(( (exp_timestamp - current_timestamp) / 86400 ))
                
                if [ "$days_left" -lt 30 ]; then
                    warn "SSL证书即将过期: $cert_file ($days_left 天)"
                else
                    log "SSL证书有效: $cert_file ($days_left 天)"
                fi
            fi
        done
    fi
}

# 性能测试
performance_test() {
    log "⚡ 执行性能测试..."
    
    # 简单的API性能测试
    if command -v ab >/dev/null 2>&1; then
        log "执行API性能测试 (10个请求)..."
        ab -n 10 -c 2 -q http://localhost:5000/api/auth/login > /tmp/perf_test.log 2>&1
        
        # 提取关键指标
        requests_per_sec=$(grep "Requests per second" /tmp/perf_test.log | awk '{print $4}')
        time_per_request=$(grep "Time per request" /tmp/perf_test.log | head -1 | awk '{print $4}')
        
        log "API性能: ${requests_per_sec} req/sec, 平均响应时间: ${time_per_request}ms"
        
        rm -f /tmp/perf_test.log
    else
        log "未安装ab工具，跳过性能测试"
    fi
}

# 生成健康报告
generate_report() {
    log "📄 生成健康检查报告..."
    
    report_file="health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=================================="
        echo "企业管理系统健康检查报告"
        echo "生成时间: $(date)"
        echo "=================================="
        echo ""
        
        echo "系统信息:"
        echo "主机名: $(hostname)"
        echo "系统负载: $(uptime)"
        echo "磁盘使用: $(df -h / | awk 'NR==2 {print $5}')"
        echo "内存使用: $(free -h | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')"
        echo ""
        
        echo "Docker信息:"
        echo "Docker版本: $(docker --version)"
        echo "Compose版本: $(docker-compose --version)"
        echo ""
        
        echo "容器状态:"
        docker-compose -f docker-compose.prod.yml ps
        echo ""
        
        echo "网络状态:"
        docker network ls | grep company
        echo ""
        
    } > "logs/$report_file"
    
    log "健康检查报告已保存: logs/$report_file"
}

# 修复建议
suggest_fixes() {
    log "💡 修复建议..."
    
    echo "常见问题修复:"
    echo "1. 重启所有服务: docker-compose -f docker-compose.prod.yml restart"
    echo "2. 查看详细日志: docker-compose -f docker-compose.prod.yml logs -f [service_name]"
    echo "3. 重新构建镜像: docker-compose -f docker-compose.prod.yml build --no-cache"
    echo "4. 清理Docker资源: docker system prune -f"
    echo "5. 检查防火墙设置: sudo ufw status"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "     企业管理系统 - 健康检查"
    echo "======================================"
    echo -e "${NC}"
    
    # 创建日志目录
    mkdir -p logs
    
    # 执行健康检查
    local checks_passed=0
    local total_checks=8
    
    check_docker_services && ((checks_passed++)) || true
    check_containers && ((checks_passed++)) || true
    check_network && ((checks_passed++)) || true
    check_database && ((checks_passed++)) || true
    check_backend && ((checks_passed++)) || true
    check_frontend && ((checks_passed++)) || true
    check_disk_usage && ((checks_passed++)) || true
    check_memory_usage && ((checks_passed++)) || true
    
    # 额外检查
    check_logs
    check_ssl
    performance_test
    
    echo ""
    echo "======================================"
    
    if [ $checks_passed -eq $total_checks ]; then
        log "🎉 健康检查通过 ($checks_passed/$total_checks)"
        generate_report
    else
        warn "⚠️  健康检查警告 ($checks_passed/$total_checks 通过)"
        suggest_fixes
        generate_report
        exit 1
    fi
}

# 错误处理
trap 'error "健康检查过程中发生错误"; exit 1' ERR

# 执行主函数
main "$@"