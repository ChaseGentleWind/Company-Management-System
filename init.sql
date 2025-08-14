-- 数据库初始化脚本
-- 企业管理系统生产环境数据库初始化

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS internal_system_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE internal_system_db;

-- 设置时区
SET time_zone = '+08:00';

-- 创建应用用户（如果不存在）
-- CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'SecurePassword123!';
-- GRANT ALL PRIVILEGES ON internal_system_db.* TO 'admin'@'%';
-- FLUSH PRIVILEGES;

-- 插入一些初始化数据（如果需要）
-- 例如：默认配置、系统参数等

-- 日志记录
INSERT IGNORE INTO mysql.general_log (event_time, user_host, thread_id, server_id, command_type, argument) 
VALUES (NOW(), 'init_script@localhost', CONNECTION_ID(), @@server_id, 'Query', 'Database initialized for Company Management System');