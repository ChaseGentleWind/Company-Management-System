# ---- Stage 1: Build Stage ----
# 使用兼容性更好的slim版本作为构建环境
FROM node:18-slim AS build

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm cache clean --force && npm install

# 复制项目所有文件
COPY . .

# 执行构建命令，生成静态文件到 /app/dist
RUN npm run build

# ---- Stage 2: Production Stage ----
# 使用轻量的Nginx镜像作为生产环境
FROM nginx:stable-alpine

# 从构建阶段复制打包好的静态文件到Nginx的默认网站目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制自定义的Nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]