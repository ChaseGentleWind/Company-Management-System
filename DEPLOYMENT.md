# 🐳 企业管理系统 - Linux Docker部署指南

## 📋 部署前准备

### 系统要求
- Linux服务器 (Ubuntu 18.04+ / CentOS 7+ / Debian 9+)
- Docker 20.10+
- Docker Compose 1.29+
- 至少 4GB RAM
- 至少 20GB 可用磁盘空间

### 安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🚀 部署步骤

### 1. 上传项目文件
将项目文件上传到Linux服务器，推荐路径：`/opt/company-system/`

### 2. 配置环境变量
编辑 `.env.production` 文件，修改数据库密码和密钥：

```bash
# 修改为强密码
SECRET_KEY=your_production_secret_key_here
JWT_SECRET_KEY=your_production_jwt_secret_key_here
MYSQL_PASSWORD=your_strong_password_here
MYSQL_ROOT_PASSWORD=your_root_password_here
```

### 3. 设置脚本权限
```bash
chmod +x deploy.sh
chmod +x health-check.sh  
chmod +x manage.sh
```

### 4. 执行部署
```bash
./deploy.sh
```

### 5. 创建管理员用户
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py create-admin admin your_password
```

## 🔧 日常管理命令

```bash
# 查看服务状态
./manage.sh status

# 查看日志
./manage.sh logs [服务名]

# 重启服务
./manage.sh restart

# 健康检查
./manage.sh health

# 备份数据库
./manage.sh backup
```

## 🌐 访问信息

- 前端访问: http://your-server-ip
- API文档: http://your-server-ip/api
- 数据库: your-server-ip:3306

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo fuser -k 80/tcp
   ```

2. **权限问题**
   ```bash
   sudo chown -R $USER:$USER .
   ```

3. **内存不足**
   ```bash
   free -h
   docker system prune -f
   ```

4. **查看详细错误日志**
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

### 服务重置

如果需要完全重置：
```bash
# 停止所有服务
./manage.sh stop

# 删除所有容器和数据
docker-compose -f docker-compose.prod.yml down -v

# 清理Docker资源
docker system prune -a -f

# 重新部署
./deploy.sh
```

## 🔒 安全建议

1. **修改默认密码**: 确保修改所有默认密码
2. **防火墙配置**: 只开放必要端口
3. **SSL证书**: 配置HTTPS证书
4. **定期备份**: 设置自动备份任务
5. **日志监控**: 定期检查应用日志

## 📊 监控和维护

### 自动健康检查
```bash
# 添加到crontab，每10分钟检查一次
*/10 * * * * /opt/company-system/health-check.sh >> /var/log/health-check.log 2>&1
```

### 自动备份
```bash
# 每天凌晨2点自动备份
0 2 * * * /opt/company-system/manage.sh backup
```

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件: `logs/` 目录
2. 健康检查报告: `logs/health_report_*.txt`
3. Docker容器状态: `docker-compose -f docker-compose.prod.yml ps`