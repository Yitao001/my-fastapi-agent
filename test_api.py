#!/usr/bin/env python3
"""
API测试脚本
演示如何正确调用人物画像分析API
"""
import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 获取API Key
    api_key = os.getenv("API_KEY", "")
    
    # 构建请求头
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    
    print("=" * 60)
    print("人物画像分析API测试")
    print("=" * 60)
    print(f"API Key: {'已配置' if api_key else '未配置（开发模式）'}")
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    try:
        response = requests.get(f"{base_url}/health", headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=4)}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 2. 正确的请求格式
    print("\n2. 测试正确的请求格式...")
    correct_payload = {
        "participant_id": "S2023003"
    }
    print(f"   请求体: {json.dumps(correct_payload, ensure_ascii=False, indent=4)}")
    
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json=correct_payload,
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=4)}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 3. 测试错误的请求格式（用于演示）
    print("\n3. 测试错误的请求格式（演示用）...")
    wrong_payload = {
        "student_id": "S2023003"  # 错误的字段名
    }
    print(f"   请求体: {json.dumps(wrong_payload, ensure_ascii=False, indent=4)}")
    
    try:
        response = requests.post(
            f"{base_url}/analyze",
            json=wrong_payload,
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=4)}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 4. 测试无API Key（如果配置了的话）
    if api_key:
        print("\n4. 测试无API Key访问（应该失败）...")
        try:
            response = requests.post(
                f"{base_url}/analyze",
                json=correct_payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=4)}")
        except Exception as e:
            print(f"   错误: {e}")
    
    print("\n" + "=" * 60)
    print("API文档地址:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    print("\n重要提示:")
    print("  - 正确的字段名是: participant_id")
    print("  - 请求头需要包含: Content-Type: application/json")
    print("  - 如果配置了API Key，还需要: X-API-Key: your_key")
    print("  - 请访问 /docs 查看交互式API文档")

if __name__ == "__main__":
    main()
