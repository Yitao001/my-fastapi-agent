# 学生画像分析智能体 - 完整使用指南

## 📋 目录

1. [项目简介](#项目简介)
2. [系统架构](#系统架构)
3. [部署者指南（部署智能体服务）](#部署者指南部署智能体服务)
4. [用户指南（使用智能体服务）](#用户指南使用智能体服务)
5. [API文档](#api文档)
6. [常见问题](#常见问题)
7. [技术支持](#技术支持)

---

## 项目简介

学生画像分析智能体是一个基于AI的系统，通过分析学生的历史谈话记录，自动生成学生的人物画像，帮助教育工作者更好地了解学生的性格、学习情况和心理状态。

---

## 系统架构

```
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│  AI智能体服务    │  ──────→│  数据库代理服务     │  ──────→│  用户数据库      │
│  (云端服务器)    │  API    │  (用户本地运行)     │         │  (用户本地)      │
└─────────────────┘         └─────────────────────┘         └─────────────────┘
```

### 安全特点

- ✅ **数据不出用户环境**：您的学生数据永远在本地，不会上传到云端
- ✅ **智能体不碰敏感数据**：AI只分析数据，不存储任何学生信息
- ✅ **双重API Key认证**：保障数据访问安全
- ✅ **企业级合规**：符合等保和数据安全法要求

---

## 部署者指南（部署智能体服务）

### 前置要求

- 阿里云ECS服务器（或其他云服务器）
- Python 3.10+
- Git
- 通义千问API Key（或其他大模型API Key）

### 第1步：克隆项目

```bash
git clone https://github.com/Yitao001/my-fastapi-agent.git
cd my-fastapi-agent
```

### 第2步：创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 第3步：安装依赖

```bash
pip install -r requirements.txt
```

### 第4步：配置环境变量

```bash
cp .env.example .env
vim .env
```

填写以下配置：

```env
# ==========================================
# 模型配置
# ==========================================
MODEL_PROVIDER=tongyi
CHAT_MODEL_NAME=qwen-max
EMBEDDING_MODEL_NAME=text-embedding-v4

# ==========================================
# 数据库代理服务配置
# ==========================================
PROXY_API_URL=http://localhost:8001  # 测试时用，实际部署时改为用户代理地址
PROXY_API_KEY=test_proxy_key_123

# ==========================================
# API安全配置
# ==========================================
API_KEY=your_secure_api_key_change_this
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# ==========================================
# 限流配置
# ==========================================
RATE_LIMIT_PER_MINUTE=60

# ==========================================
# 通义千问API Key（必需！）
# ==========================================
DASHSCOPE_API_KEY=sk-your-dashscope-api-key
```

### 第5步：启动服务

```bash
# 直接启动
python api.py

# 或使用 nohup 后台运行
nohup python api.py > server.log 2>&1 &

# 查看日志
tail -f server.log
```

### 第6步：验证部署

1. 访问：`http://your-server-ip:8000/docs`
2. 点击 **Authorize**，输入您的 API Key
3. 测试 `/health/lite` 端点，应该返回 `{"status": "ok"}`

### 部署 db-proxy 给用户

将 `db-proxy/` 目录打包并分发给用户：

```bash
zip -r db-proxy.zip db-proxy/
```

---

## 用户指南（使用智能体服务）

### 第1步：下载并解压

1. 从我们提供的链接下载 `db-proxy.zip` 文件
2. 解压到您电脑的任意位置，比如 `D:\db-proxy`

### 第2步：配置数据库连接

1. 进入 `db-proxy` 文件夹
2. 找到 `.env.example` 文件，复制一份并重命名为 `.env`
3. 用记事本打开 `.env` 文件，填写您的数据库信息：

```env
# ==========================================
# 代理API Key（由智能体服务提供方提供）
# ==========================================
PROXY_API_KEY=test_proxy_key_123  # 请使用我们提供的真实Key

# ==========================================
# 您的数据库配置
# ==========================================
MYSQL_HOST=localhost  # 数据库地址，通常是localhost
MYSQL_PORT=3306       # 数据库端口，默认3306
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
```

### 第3步：启动数据库代理服务

#### Windows用户
- 双击运行 `start.bat` 文件
- 看到 "数据库代理服务启动中..." 的提示即成功

#### Mac/Linux用户
- 打开终端，进入 `db-proxy` 目录
- 运行：`chmod +x start.sh && ./start.sh`

### 第4步：获取您的代理服务地址

启动成功后，您会看到：
```
API文档: http://localhost:8001/docs
```

**重要**：如果智能体服务在云端，您需要：
- 使用内网穿透工具（如 ngrok）
- 或配置路由器端口转发
- 将公网地址提供给智能体服务提供方

### 第5步：配置智能体访问您的代理

将您的代理服务地址提供给智能体服务提供方，他们会更新配置。

---

## 数据库配置（重要！）

### 方案A：使用现有数据库

如果您已经有学生谈话记录数据库，请确保：

1. **表结构要求**：
   - 表名：`talk_record`（或在 `.env` 中配置）
   - 必需字段：
     - `student_id`：学生唯一标识
     - `content`：谈话内容
     - `created_time`：创建时间（DATETIME类型）

2. **权限设置**：
   - 建议创建只读用户，只赋予 `SELECT` 权限
   - 例如：
     ```sql
     CREATE USER 'proxy_user'@'localhost' IDENTIFIED BY 'your_password';
     GRANT SELECT ON student_db.talk_record TO 'proxy_user'@'localhost';
     ```

### 方案B：创建新数据库

如果您没有数据库，我们提供了示例表结构：

1. 登录MySQL：
   ```bash
   mysql -u root -p
   ```

2. 执行 `example_schema.sql` 中的SQL语句：
   ```sql
   -- 创建数据库
   CREATE DATABASE IF NOT EXISTS student_db CHARACTER SET utf8mb4;
   
   -- 使用数据库
   USE student_db;
   
   -- 创建表
   CREATE TABLE IF NOT EXISTS talk_record (
       id INT AUTO_INCREMENT PRIMARY KEY,
       student_id VARCHAR(50) NOT NULL,
       content TEXT NOT NULL,
       created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
       INDEX idx_student_id (student_id)
   );
   
   -- 插入测试数据
   INSERT INTO talk_record (student_id, content, created_time) VALUES
   ('S2023001', '今天学习了数学，感觉有点难，特别是几何部分。', '2026-04-01 09:00:00'),
   ('S2023001', '老师布置了新的作业，我会认真完成的。', '2026-04-02 14:30:00'),
   ('S2023001', '今天考试了，希望能有个好成绩。', '2026-04-03 16:00:00'),
   ('S2023002', '我喜欢上体育课，今天跑了800米。', '2026-04-01 10:00:00'),
   ('S2023003', '最近在读一本有趣的书，讲的是历史故事。', '2026-04-01 11:00:00'),
   ('S2023003', '周末计划去图书馆看书，顺便复习功课。', '2026-04-02 16:00:00');
   ```

---

## 测试您的代理服务

1. 打开浏览器，访问：`http://localhost:8001/docs`
2. 点击右上角的 **Authorize**，输入 `PROXY_API_KEY`
3. 找到 `POST /chat-history` 接口
4. 点击 **Try it out**
5. 输入学生ID，例如：
   ```json
   {
     "student_id": "S2023001",
     "limit": 10
   }
   ```
6. 点击 **Execute**，如果能看到返回的对话历史，说明代理服务正常！

---

## 使用智能体进行学生画像分析

### 第1步：访问智能体服务

在浏览器打开：`http://your-server-ip:8000/docs`

### 第2步：配置API Key

1. 点击右上角的 **Authorize**
2. 输入您的 API Key
3. 点击 **Authorize** 完成认证

### 第3步：生成学生画像

1. 找到 `POST /analyze` 接口
2. 点击 **Try it out**
3. 输入请求参数：
   ```json
   {
     "participant_id": "S2023001",
     "participant_name": "张三"
   }
   ```
4. 点击 **Execute**
5. 等待几秒钟，AI会返回详细的学生画像分析！

---

## 学生画像分析示例

### 输入：
```json
{
  "participant_id": "S2023001",
  "participant_name": "张三"
}
```

### 输出：
```json
{
  "status": "success",
  "data": "张三是一个勤奋好学的学生，对学习有较高的要求和期望。从对话中可以看出，他在数学学习上遇到了一些困难，特别是几何部分，但他表现出积极的学习态度，会认真完成老师布置的作业。他对考试结果很在意，希望能取得好成绩，显示出较强的上进心和自我要求。整体来看，张三是一个目标明确、态度端正的学生，需要在数学学习上得到更多的支持和指导。",
  "message": "人物画像分析成功"
}
```

---

## API文档

### 智能体服务 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 完整健康检查（数据库+LLM） |
| `/health/lite` | GET | 轻量级健康检查 |
| `/status` | GET | 系统状态 |
| `/cache/clear` | POST | 清空缓存 |
| `/analyze` | POST | 分析学生画像 |

### 数据库代理服务 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/chat-history` | POST | 获取对话历史 |

---

## 常见问题与解决方案

### 问题1：代理服务启动失败
**症状**：运行 `start.bat` 后出现错误
**解决方案**：
- 检查Python是否安装：`python --version`
- 检查数据库是否启动：`net start mysql`（Windows）
- 检查数据库连接信息是否正确

### 问题2：智能体返回 "代理服务调用失败"
**症状**：智能体调用时出现代理服务错误
**解决方案**：
- 确认代理服务是否正在运行
- 确认 `PROXY_API_URL` 是否正确
- 确认 `PROXY_API_KEY` 是否一致
- 如果智能体在云端，需要配置内网穿透

### 问题3：数据库连接失败
**症状**：代理服务日志显示 "数据库错误"
**解决方案**：
- 检查数据库用户名密码是否正确
- 检查数据库服务是否启动
- 检查防火墙是否阻止连接

### 问题4：返回 "未找到历史会谈信息"
**症状**：智能体返回没有找到对话历史
**解决方案**：
- 检查学生ID是否存在于数据库中
- 检查表名和字段名配置是否正确
- 检查数据库中是否有该学生的记录

### 问题5：如何更换大模型？
**解决方案**：
- 修改 `.env` 文件中的 `MODEL_PROVIDER`、`CHAT_MODEL_NAME`
- 配置对应的 API Key
- 重启服务

---

## 性能优化建议

1. **数据库索引**：为 `student_id` 和 `created_time` 字段添加索引
2. **查询限制**：建议单次查询限制在100条以内
3. **网络优化**：如果网络较慢，考虑使用内网穿透工具
4. **缓存策略**：系统已内置缓存，相同学生ID的分析结果会被缓存

---

## 安全最佳实践

1. **使用只读用户**：数据库用户只赋予SELECT权限
2. **定期更换API Key**：每3-6个月更换一次 `PROXY_API_KEY`
3. **网络隔离**：在防火墙中限制代理服务的访问IP
4. **日志管理**：定期清理代理服务日志，避免敏感信息泄露
5. **HTTPS加密**：生产环境建议使用HTTPS

---

## 技术支持

如果您遇到任何问题，请联系我们：
- 邮箱：support@example.com
- 电话：400-123-4567
- 工作时间：周一至周五 9:00-18:00

---

## 祝您使用愉快！

学生画像分析智能体将帮助您更好地了解学生，为教育教学提供有力支持！
