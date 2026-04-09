#!/usr/bin/env python3
"""
数据库代理客户端（用户端）
连接云服务器中继服务，执行本地数据库查询
"""
import asyncio
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import websockets
from datetime import datetime

load_dotenv()

RELAY_URL = os.getenv("RELAY_URL", "ws://localhost:8002")
CLIENT_ID = os.getenv("CLIENT_ID", "client_001")

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "student_talk_db")


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None


def execute_query(query, params=None):
    """执行 SQL 查询"""
    connection = get_db_connection()
    if not connection:
        return {"status": "error", "error": "数据库连接失败"}
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"status": "success", "data": results}
    except Error as e:
        return {"status": "error", "error": str(e)}


async def handle_request(request):
    """处理来自中继的请求"""
    action = request.get("action")
    params = request.get("params", {})
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 收到请求: {action}")
    
    try:
        if action == "chat_history":
            student_id = params.get("student_id", "")
            limit = params.get("limit", 100)
            
            query = """
                SELECT content, created_time 
                FROM chat_records 
                WHERE student_id = %s 
                ORDER BY created_time ASC 
                LIMIT %s
            """
            result = execute_query(query, (student_id, limit))
            return result
            
        elif action == "health_check":
            connection = get_db_connection()
            if connection:
                connection.close()
                return {"status": "success", "data": {"database": "ok"}}
            else:
                return {"status": "error", "error": "数据库连接失败"}
        else:
            return {"status": "error", "error": f"未知的操作: {action}"}
            
    except Exception as e:
        print(f"处理请求出错: {e}")
        return {"status": "error", "error": str(e)}


async def main():
    """主函数"""
    print("=" * 60)
    print("数据库代理客户端启动中...")
    print("=" * 60)
    print(f"客户端ID: {CLIENT_ID}")
    print(f"中继服务: {RELAY_URL}")
    print(f"数据库: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    print("=" * 60)
    
    while True:
        try:
            ws_url = f"{RELAY_URL}/ws/client/{CLIENT_ID}"
            print(f"正在连接中继服务: {ws_url}")
            
            async with websockets.connect(ws_url) as websocket:
                print(f"已连接到中继服务: {CLIENT_ID}")
                
                while True:
                    try:
                        message = await websocket.recv()
                        request = json.loads(message)
                        request_id = request.get("request_id")
                        
                        response = await handle_request(request)
                        response["request_id"] = request_id
                        
                        await websocket.send(json.dumps(response))
                        
                    except websockets.exceptions.ConnectionClosed:
                        print("与中继服务的连接已断开")
                        break
                    except Exception as e:
                        print(f"处理消息出错: {e}")
                        error_response = {
                            "request_id": request.get("request_id", ""),
                            "status": "error",
                            "error": str(e)
                        }
                        try:
                            await websocket.send(json.dumps(error_response))
                        except:
                            pass
                        
        except Exception as e:
            print(f"连接失败: {e}")
            print("5秒后尝试重新连接...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
