# 数据库代理服务 - 用户部署指南

## 📦 简介

这是数据库代理服务，用于安全地连接您的本地数据库，让AI智能体通过代理访问数据，而不用直接暴露您的数据库。

## 🛡️ 安全特性

- ✅ 您的数据库永远在内网
- ✅ AI智能体不直接访问您的数据库
- ✅ API Key认证保护
- ✅ 可配置只读查询
- ✅ 符合数据安全要求

---

## 🚀 快速开始

### Windows用户

1. **解压文件**
   把 `db-proxy` 文件夹放到您想放的位置

2. **配置数据库连接**
   复制 `.env.example` 为 `.env`
   ```cmd
   copy .env.example .env
   ```
   
   编辑 `.env` 文件，填入您的数据库信息：
   ```env
   # 代理API Key（从AI服务提供方获取）
   PROXY_API_KEY=your_proxy_api_key_here
   
   # 您的数据库配置
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=your_db_user
   MYSQL_PASSWORD=your_db_password
   MYSQL_DATABASE=your_db_name
   
   # 表结构配置
   TABLE_NAME=talk_record
   STUDENT_ID_FIELD=student_id
   CONTENT_FIELD=content
   CREATED_TIME_FIELD=created_time
   ```

3. **启动服务**
   双击运行 `start.bat`

### Linux/Mac用户

1. **解压文件**
   ```bash
   cd db-proxy
   ```

2. **配置数据库连接**
   ```bash
   cp .env.example .env
   vim .env
   ```
   
   填入您的数据库信息（同Windows）

3. **启动服务**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

---

## 📋 配置说明

### .env 配置项

| 参数 | 必填 | 说明 |
|------|------|------|
| `PROXY_API_KEY` | ✅ | AI服务提供方给您的代理API Key |
| `MYSQL_HOST` | ✅ | 您的数据库地址（通常是 localhost） |
| `MYSQL_PORT` | ✅ | 数据库端口（默认 3306） |
| `MYSQL_USER` | ✅ | 数据库用户名 |
| `MYSQL_PASSWORD` | ✅ | 数据库密码 |
| `MYSQL_DATABASE` | ✅ | 数据库名 |
| `TABLE_NAME` | ✅ | 谈话记录表名 |
| `STUDENT_ID_FIELD` | ✅ | 学生ID字段名 |
| `CONTENT_FIELD` | ✅ | 内容字段名 |
| `CREATED_TIME_FIELD` | ✅ | 创建时间字段名 |
| `QUERY_LIMIT` | ❌ | 单次查询最大条数（默认100） |

---

## 🔍 验证服务

启动成功后，在浏览器访问：

```
http://localhost:8001/docs
```

您会看到Swagger API文档，可以测试接口。

---

## 📡 网络配置

### 场景1：AI服务和代理在同一台机器

无需额外配置，使用默认 `http://localhost:8001` 即可。

### 场景2：AI服务在远程服务器

1. 确保您的机器可以被远程访问
2. 修改防火墙，开放8001端口
3. 把 `PROXY_API_URL` 改成您的机器IP：`http://your-ip:8001`
4. 建议配置防火墙，只允许AI服务的IP访问8001端口

---

## 🔐 安全建议

1. **使用只读数据库用户**
   创建一个只读账号给代理服务使用，不要用root账号。

2. **限制IP访问**
   在防火墙中只允许AI服务的IP访问8001端口。

3. **定期更换API Key**
   和AI服务提供方约定定期更换 `PROXY_API_KEY`。

---

## 📞 技术支持

如有问题，请联系AI服务提供方。
