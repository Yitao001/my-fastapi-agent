# 数据库代理中继服务

## 架构说明

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   智能体    │  HTTP   │   中继服务  │WebSocket │   客户端    │
│  (云服务器) │────────▶│  (云服务器) │◀────────│  (用户内网) │
│             │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
                                                    │
                                                    ▼
                                              ┌─────────────┐
                                              │  本地数据库  │
                                              └─────────────┘
```

## 部署步骤

### 1. 云服务器：部署中继服务

```bash
cd relay
cp .env.example .env
# 编辑 .env 设置 RELAY_API_KEY

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

中继服务默认监听端口：**8002**

---

### 2. 用户端：部署客户端程序

```bash
cd db-proxy-client
cp .env.example .env
# 编辑 .env 设置：
#   - RELAY_URL: 中继服务地址（ws://your-server-ip:8002）
#   - CLIENT_ID: 客户端唯一标识
#   - 数据库配置

# 安装依赖
pip install -r requirements.txt

# 启动客户端
python client.py
# 或双击 start.bat（Windows）
```

---

### 3. 智能体配置

在智能体的 `.env` 文件中添加：

```env
# 启用中继模式
RELAY_MODE=true
RELAY_API_URL=http://your-server-ip:8002
RELAY_API_KEY=relay_secret_key_123
RELAY_CLIENT_ID=client_001
```

---

## 优势

1. **无需公网 IP**：用户无需开放端口或使用内网穿透
2. **更安全**：连接由用户主动发起，防火墙只需允许出站
3. **永久在线**：客户端可设置为开机自启服务
4. **易于部署**：用户只需双击运行客户端

---

## API 文档

启动中继服务后访问：`http://your-server:8002/docs`
