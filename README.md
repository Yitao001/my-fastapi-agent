# 人物画像分析智能体 - 企业级安全架构

## 🎯 核心架构

```
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│  AI智能体服务    │  ──────→│  数据库代理服务     │  ──────→│  用户数据库      │
│  (您的服务器)    │  API    │  (用户内网运行)     │         │  (用户本地)      │
└─────────────────┘         └─────────────────────┘         └─────────────────┘
```

## 🛡️ 安全优势

- ✅ **数据不出用户环境**：用户数据库永远在内网
- ✅ **智能体不碰敏感数据**：只提供AI能力，不存储用户业务数据
- ✅ **API Key认证**：双重安全认证
- ✅ **企业级合规**：符合等保和数据安全法要求

---

## 📦 部署方案

### 方案一：您部署智能体服务

1. 在您的服务器上部署AI智能体
2. 提供数据库代理服务给用户
3. 用户在本地运行代理服务

### 方案二：用户部署代理服务

1. 把 `db-proxy/` 目录发给用户
2. 用户在本地配置数据库连接
3. 用户启动代理服务
4. 您的智能体通过代理访问用户数据

---

## 🚀 快速开始

### 1. 部署AI智能体（您的服务器）

```bash
# 克隆代码
git clone <your-repo-url>
cd my-fastapi-agent

# 安装依赖
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置 .env
cp .env.example .env
vim .env

# 启动服务
nohup python api.py > server.log 2>&1 &
```

### 2. 用户部署数据库代理

把 `db-proxy/` 目录打包发给用户，用户执行：

```bash
# 进入代理目录
cd db-proxy

# 配置环境变量
cp .env.example .env
vim .env
```

编辑 `.env` 文件：
```env
# 代理API Key（您提供给用户）
PROXY_API_KEY=your_proxy_secure_key

# 用户数据库配置
MYSQL_HOST=localhost
MYSQL_USER=user_db_user
MYSQL_PASSWORD=user_db_password
MYSQL_DATABASE=user_db_name

# 表结构配置
TABLE_NAME=talk_record
STUDENT_ID_FIELD=student_id
CONTENT_FIELD=content
CREATED_TIME_FIELD=created_time
```

启动代理服务：
```bash
pip install -r requirements.txt
python main.py
```

---

## 🔧 配置说明

### 智能体配置 (`.env`)

| 参数 | 说明 | 示例 |
|------|------|------|
| `PROXY_API_URL` | 用户代理服务地址 | `http://user-proxy-ip:8001` |
| `PROXY_API_KEY` | 代理API Key（与用户一致） | `proxy_secure_key_123` |
| `API_KEY` | 智能体API Key | `your_api_key` |
| `DASHSCOPE_API_KEY` | 通义千问API Key | `sk-xxxxxx` |

### 代理配置 (`db-proxy/.env`)

| 参数 | 说明 |
|------|------|
| `PROXY_API_KEY` | 代理API Key（与智能体一致） |
| `MYSQL_HOST` | 用户数据库地址 |
| `MYSQL_USER` | 用户数据库用户名 |
| `MYSQL_PASSWORD` | 用户数据库密码 |
| `MYSQL_DATABASE` | 用户数据库名 |
| `TABLE_NAME` | 谈话记录表名 |
| `STUDENT_ID_FIELD` | 学生ID字段名 |
| `CONTENT_FIELD` | 内容字段名 |
| `CREATED_TIME_FIELD` | 创建时间字段名 |

---

## 📊 API文档

### 智能体API

访问：`http://your-ecs-ip:8000/docs`

### 代理API

访问：`http://user-proxy-ip:8001/docs`

---

## 🔐 安全建议

1. **使用HTTPS**：生产环境启用HTTPS
2. **API Key轮换**：定期更换API Key
3. **网络限制**：在用户侧限制代理服务的访问IP
4. **只读用户**：用户数据库使用只读账号

---

## 📞 技术支持

如有问题，请联系技术支持。
