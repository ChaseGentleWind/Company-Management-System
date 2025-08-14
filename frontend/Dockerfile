# ---- Stage 1: Build Stage ----
# 使用兼容性更好的slim版本作为构建环境
FROM node:18-slim AS build

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖 - 优化npm安装
RUN npm ci --only=production && npm cache clean --force

# 复制项目所有文件
COPY . .

# 执行构建命令，生成静态文件到 /app/dist
RUN npm run build

# ---- Stage 2: Production Stage ----
# 使用轻量的Nginx镜像作为生产环境
FROM nginx:stable-alpine

# 安装curl用于健康检查
RUN apk --no-cache add curl

# 从构建阶段复制打包好的静态文件到Nginx的默认网站目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制自定义的Nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 创建nginx用户和设置权限
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# 切换到nginx用户
USER nginx

# 暴露80端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/api/health || exit 1

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]