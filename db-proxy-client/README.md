# 数据库代理客户端 - 使用教程

## 目录
1. [快速开始](#1-快速开始)
2. [配置说明](#2-配置说明)
3. [中继服务测试](#3-中继服务测试)
4. [智能体 API 测试](#4-智能体-api-测试)
5. [常见问题](#5-常见问题)

---

## 1. 快速开始

### 1.1 环境要求
- Python 3.8+
- Windows / Linux / Mac

### 1.2 安装步骤

#### Windows 用户
1. 解压本文件夹
2. 双击运行 `start.bat`
3. 首次运行会自动创建 `.env` 文件
4. 用记事本打开 `.env`，修改配置
5. 再次双击 `start.bat`

#### Mac / Linux 用户
```bash
# 1. 进入文件夹
cd db-proxy-client

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑配置
vim .env

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行客户端
python client.py
```

---

## 2. 配置说明

编辑 `.env` 文件：

```env
# ==========================================
# 中继服务配置
# ==========================================
RELAY_URL=ws://47.102.145.89:8002  # 云服务器中继服务地址
CLIENT_ID=my_client_001                # 您的客户端唯一标识

# ==========================================
# 数据库配置
# ==========================================
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=student_talk_db
```

### 配置项详解

| 配置项 | 说明 | 示例 |
|--------|------|------|
| RELAY_URL | 云服务器中继服务的 WebSocket 地址 | ws://your-server:8002 |
| CLIENT_ID | 您的客户端唯一标识（可以自己命名） | school_a_client |
| MYSQL_HOST | 数据库地址 | 127.0.0.1 |
| MYSQL_PORT | 数据库端口 | 3306 |
| MYSQL_USER | 数据库用户名 | root |
| MYSQL_PASSWORD | 数据库密码 | your_password |
| MYSQL_DATABASE | 数据库名称 | student_talk_db |

---

## 3. 中继服务测试

### 3.1 启动客户端
运行客户端后，看到以下信息表示连接成功：

```
============================================================
数据库代理客户端启动中...
============================================================
客户端ID: my_client_001
中继服务: ws://47.102.145.89:8002
数据库: 127.0.0.1:3306/student_talk_db
============================================================
正在连接中继服务: ws://47.102.145.89:8002/ws/client/my_client_001
已连接到中继服务: my_client_001
```

### 3.2 验证客户端在线
联系服务提供方，他们可以通过中继服务的 API 查看您的客户端是否在线：

```
GET http://your-server:8002/clients
```

应该会返回您的 `CLIENT_ID`。

---

## 4. 智能体 API 测试

### 4.1 获取 API Key
从服务提供方获取您的 API Key。

### 4.2 访问 API 文档
在浏览器中打开：
```
http://your-server:8000/docs
```

### 4.3 测试步骤

#### 第1步：认证
1. 点击右上角的 **Authorize**
2. 输入您的 API Key
3. 点击 **Authorize** 完成认证

#### 第2步：测试健康检查
找到 `GET /health/lite` 接口，点击 **Try it out**，然后 **Execute**。

预期响应：
```json
{
  "status": "ok"
}
```

#### 第3步：测试学生画像分析
找到 `POST /analyze/simple` 接口，点击 **Try it out**，输入：

```json
{
  "participant_id": "test_student_001"
}
```

点击 **Execute**，等待几秒钟，AI会返回学生画像分析结果。

### 4.4 使用 curl 测试

```bash
# 测试健康检查
curl -X GET "http://your-server:8000/health/lite"

# 测试学生画像分析
curl -X POST "http://your-server:8000/analyze/simple" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"participant_id": "test_student_001"}'
```

---

## 5. 常见问题

### Q1: 客户端连接中继服务失败？
**A:** 检查以下几点：
1. 网络连接是否正常
2. `RELAY_URL` 是否正确
3. 防火墙是否阻止了 WebSocket 连接
4. 中继服务是否正常运行

### Q2: 数据库连接失败？
**A:** 检查：
1. MySQL 服务是否启动
2. 用户名密码是否正确
3. 数据库名称是否正确
4. 用户是否有访问该数据库的权限

### Q3: 如何确认客户端正在运行？
**A:** 看客户端窗口是否显示"已连接到中继服务"。

### Q4: 如何查看日志？
**A:** 客户端窗口会实时显示日志信息。

### Q5: 可以在多台电脑上运行客户端吗？
**A:** 可以！每台电脑使用不同的 `CLIENT_ID` 即可。

### Q6: 数据安全吗？
**A:** 非常安全！
- 您的数据永远在本地，不会上传到云端
- 连接由您主动发起，服务提供方无法主动访问您的内网
- 只有授权的请求才会查询您的数据库

---

## 6. 数据库表结构要求

如果您还没有学生谈话记录表，请按以下结构创建：

```sql
CREATE TABLE chat_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id)
);
```

### 字段说明
- `student_id`: 学生唯一标识
- `content`: 谈话内容
- `created_time`: 创建时间

---

## 7. 技术支持

如果您遇到任何问题，请联系我们的技术支持团队。

---

**祝您使用愉快！**
