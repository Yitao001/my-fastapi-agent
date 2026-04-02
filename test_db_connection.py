#!/usr/bin/env python3
"""
数据库连接测试脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_handler import db_conf
import mysql.connector
from mysql.connector import Error

def test_database_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)
    
    # 读取配置
    mysql_config = db_conf.get("mysql", {})
    table_config = db_conf.get("table_structure", {})
    
    print(f"\n数据库配置:")
    print(f"  主机: {mysql_config.get('host')}")
    print(f"  用户: {mysql_config.get('user')}")
    print(f"  数据库: {mysql_config.get('database')}")
    print(f"\n表结构配置:")
    print(f"  表名: {table_config.get('table_name')}")
    print(f"  字段映射: {table_config.get('fields')}")
    
    try:
        # 尝试连接数据库
        print("\n1. 尝试连接数据库...")
        conn = mysql.connector.connect(
            host=mysql_config.get("host", "localhost"),
            user=mysql_config.get("user", "root"),
            password=mysql_config.get("password", ""),
            database=mysql_config.get("database", "chat_history")
        )
        print("   [OK] 数据库连接成功！")
        
        cursor = conn.cursor()
        
        # 检查表是否存在
        table_name = table_config.get("table_name", "talk_record")
        print(f"\n2. 检查表 '{table_name}' 是否存在...")
        
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        
        if result:
            print(f"   [OK] 表 '{table_name}' 存在！")
        else:
            print(f"   [ERROR] 表 '{table_name}' 不存在！")
            print(f"\n   数据库中的表列表:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                print(f"     - {table[0]}")
            return False
        
        # 查看表结构
        print(f"\n3. 查看表结构...")
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print("   字段列表:")
        for col in columns:
            print(f"     - {col[0]} ({col[1]})")
        
        # 检查必需字段
        fields = table_config.get("fields", {})
        required_fields = [
            fields.get("student_id", "student_id"),
            fields.get("content", "content"),
            fields.get("created_time", "created_time")
        ]
        
        print(f"\n4. 检查必需字段...")
        column_names = [col[0] for col in columns]
        all_found = True
        
        for field in required_fields:
            if field in column_names:
                print(f"   [OK] 字段 '{field}' 存在")
            else:
                print(f"   [ERROR] 字段 '{field}' 不存在！")
                all_found = False
        
        if not all_found:
            print(f"\n   错误：缺少必需字段！请检查配置。")
            return False
        
        # 查询一些数据
        print(f"\n5. 查询示例数据...")
        student_id_field = fields.get("student_id", "student_id")
        content_field = fields.get("content", "content")
        created_time_field = fields.get("created_time", "created_time")
        
        query = f"""
        SELECT {student_id_field}, {content_field}, {created_time_field}
        FROM {table_name}
        ORDER BY {created_time_field} DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"   [OK] 找到 {len(results)} 条记录：")
            for i, row in enumerate(results, 1):
                print(f"     {i}. ID: {row[0]}, 时间: {row[2]}")
                content_str = str(row[1])
                print(f"        内容: {content_str[:50]}..." if len(content_str) > 50 else f"        内容: {content_str}")
        else:
            print(f"   [WARN] 表中没有数据")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("数据库连接测试完成！")
        print("=" * 60)
        return True
        
    except Error as e:
        print(f"\n[ERROR] 数据库连接失败：{str(e)}")
        print("\n可能的原因:")
        print("  1. MySQL服务未启动")
        print("  2. 用户名或密码错误")
        print("  3. 数据库不存在")
        print("  4. 网络连接问题")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
