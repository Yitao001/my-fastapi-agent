# 数据库代理服务使用指南

## 🎯 什么是数据库代理服务

数据库代理服务是一个轻量级的服务，运行在用户本地，用于安全地访问用户的数据库并向智能体提供所需的数据。

## 🏗️ 工作原理

```
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│  AI智能体服务    │  ──────→│  数据库代理服务     │  ──────→│  用户数据库      │
│  (云端服务器)    │  API    │  (用户本地运行)     │         │  (用户本地)      │
└─────────────────┘         └─────────────────────┘         └─────────────────┘
```

## 📦 快速开始

### 第1步：配置环境变量

1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env` 文件，填写您的数据库信息：

```env
# ==========================================
# 代理API Key（由智能体服务提供方提供）
# ==========================================
PROXY_API_KEY=test_proxy_key_123  # 请使用真实的API Key

# ==========================================
# 您的数据库配置
# ==========================================
MYSQL_HOST=localhost  # 数据库地址
MYSQL_PORT=3306       # 数据库端口
MYSQL_USER=root       # 数据库用户名
MYSQL_PASSWORD=123456  # 数据库密码
MYSQL_DATABASE=student_db  # 数据库名

# ==========================================
# 表结构配置
# ==========================================
TABLE_NAME=talk_record  # 谈话记录表名
STUDENT_ID_FIELD=student_id  # 学生ID字段名
CONTENT_FIELD=content  # 谈话内容字段名
CREATED_TIME_FIELD=created_time  # 创建时间字段名
QUERY_LIMIT=100  # 单次查询最大条数

# ==========================================
# 服务配置
# ==========================================
HOST=0.0.0.0  # 服务监听地址
PORT=8001     # 服务端口
```

### 第2步：启动服务

#### Windows用户
- 双击运行 `start.bat` 文件
- 看到 "数据库代理服务启动中..." 的提示即成功

#### Mac/Linux用户
- 打开终端，进入 `db-proxy` 目录
- 运行：`chmod +x start.sh && ./start.sh`

### 第3步：验证服务

1. 打开浏览器，访问：`http://localhost:8001/docs`
2. 点击右上角的 **Authorize**，输入 `PROXY_API_KEY`
3. 测试 `POST /chat-history` 接口，输入学生ID：
   ```json
   {
     "student_id": "S2023001",
     "limit": 10
   }
   ```

## 🗄️ 数据库配置

### 表结构要求

**必需字段**：
- `student_id`：学生唯一标识（VARCHAR类型）
- `content`：谈话内容（TEXT类型）
- `created_time`：创建时间（DATETIME类型）

### 示例表结构

执行 `example_schema.sql` 文件中的SQL语句：

```sql
-- 创建表
CREATE TABLE IF NOT EXISTS talk_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL COMMENT '学生ID',
    content TEXT NOT NULL COMMENT '谈话内容',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_student_id (student_id),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='谈话记录表';

-- 插入测试数据
INSERT INTO talk_record (student_id, content, created_time) VALUES
('S2023001', '今天学习了数学，感觉有点难，特别是几何部分。', '2026-04-01 09:00:00'),
('S2023001', '老师布置了新的作业，我会认真完成的。', '2026-04-02 14:30:00'),
('S2023001', '今天考试了，希望能有个好成绩。', '2026-04-03 16:00:00'),
('S2023002', '我喜欢上体育课，今天跑了800米。', '2026-04-01 10:00:00'),
('S2023002', '和同学相处很好，大家都很友善。', '2026-04-02 15:00:00'),
('S2023003', '最近在读一本有趣的书，讲的是历史故事。', '2026-04-01 11:00:00'),
('S2023003', '周末计划去图书馆看书，顺便复习功课。', '2026-04-02 16:00:00'),
('S2023003', '今天的语文课很有意思，老师讲得很好。', '2026-04-03 17:00:00');
```

## 📡 API接口

### POST /chat-history

**功能**：获取学生的聊天历史

**请求参数**：
```json
{
  "student_id": "S2023001",  // 学生ID
  "limit": 100  // 限制返回条数
}
```

**响应**：
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "student_id": "S2023001",
      "content": "今天学习了数学，感觉有点难，特别是几何部分。",
      "created_time": "2026-04-01 09:00:00"
    }
  ]
}
```

### GET /health

**功能**：检查服务健康状态

**响应**：
```json
{
  "status": "healthy"
}
```

## ⚙️ 常见问题

### 问题1：服务启动失败
**解决方案**：
- 检查Python是否安装：`python --version`
- 检查数据库是否启动：`net start mysql`（Windows）
- 检查数据库连接信息是否正确

### 问题2：数据库连接失败
**解决方案**：
- 检查数据库用户名密码是否正确
- 检查数据库服务是否启动
- 检查防火墙是否阻止连接

### 问题3：API Key认证失败
**解决方案**：
- 确认 `PROXY_API_KEY` 是否正确
- 确认智能体服务使用的API Key与代理服务一致

## 🔒 安全建议

1. **使用只读用户**：数据库用户只赋予SELECT权限
2. **定期更换API Key**：每3-6个月更换一次
3. **网络隔离**：在防火墙中限制代理服务的访问IP
4. **日志管理**：定期清理日志，避免敏感信息泄露

## 📞 技术支持

如果您遇到任何问题，请联系智能体服务提供方。

## 🎉 祝您使用愉快！