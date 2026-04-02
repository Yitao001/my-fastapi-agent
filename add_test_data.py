#!/usr/bin/env python3
"""
添加测试数据到数据库
"""
import mysql.connector
from utils.config_handler import db_conf


def add_test_data():
    """
    添加测试数据到数据库
    """
    print("====================================")
    print("添加测试数据到数据库")
    print("====================================")
    
    try:
        # 从配置文件获取 MySQL 连接参数
        mysql_config = db_conf.get("mysql", {})
        conn = mysql.connector.connect(
            host=mysql_config.get("host", "localhost"),
            user=mysql_config.get("user", "root"),
            password=mysql_config.get("password", "password"),
            database=mysql_config.get("database", "chat_history")
        )
        
        cursor = conn.cursor()
        
        # 清空现有数据
        cursor.execute("DELETE FROM chat_sessions")
        conn.commit()
        print("✅ 清空现有数据成功！")
        
        # 添加测试数据
        test_data = [
            ('session_001', '1001', '张三', '我最近工作压力很大，经常加班到很晚，感觉身体吃不消了。'),
            ('session_002', '1001', '张三', '我最近和同事的关系不太好，总是因为工作意见不合而争吵。'),
            ('session_003', '1001', '张三', '我想换一份工作，但是又担心找不到更好的机会。'),
            ('session_004', '1001', '张三', '我最近失眠很严重，每天都睡不好觉，白天工作效率很低。'),
            ('session_005', '1001', '张三', '我觉得自己的能力不够，总是做不好领导交给我的任务。')
        ]
        
        cursor.executemany(
            'INSERT INTO chat_sessions (session_id, participant_id, participant_name, chat_content) VALUES (%s, %s, %s, %s)',
            test_data
        )
        
        conn.commit()
        print(f"✅ 添加测试数据成功！共添加 {len(test_data)} 条记录")
        
        # 验证数据
        cursor.execute("SELECT * FROM chat_sessions WHERE participant_id = '1001'")
        results = cursor.fetchall()
        print(f"✅ 验证数据成功！找到 {len(results)} 条记录")
        for row in results:
            print(f"  会话ID: {row[1]}, 内容: {row[4]}")
        
        conn.close()
        print("\n✅ 测试数据添加完成！")
        
    except Exception as e:
        print(f"❌ 添加测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    add_test_data()