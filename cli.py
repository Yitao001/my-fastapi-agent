#!/usr/bin/env python3
"""
命令行版本的人物画像分析工具
"""
import sys
from agent.tools.agent_tools import _generate_persona_from_db


def main():
    """
    命令行入口函数
    """
    print("====================================")
    print("人物画像分析工具")
    print("====================================")
    
    while True:
        print("\n请输入操作选项：")
        print("1. 根据ID分析人物画像")
        print("2. 退出")
        
        choice = input("请选择 (1/2): ")
        
        if choice == "1":
            participant_id = input("请输入要分析的人物ID: ")
            
            print("\n正在分析人物画像...")
            try:
                result = _generate_persona_from_db(participant_id=participant_id)
                print("\n" + "=" * 60)
                print(result)
                print("=" * 60)
            except Exception as e:
                print(f"分析失败: {str(e)}")
        
        elif choice == "2":
            print("再见！")
            break
        
        else:
            print("无效的选择，请重新输入")


if __name__ == "__main__":
    main()