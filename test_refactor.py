#!/usr/bin/env python3
"""
测试重构后的代码
"""
import sys

print("=" * 60)
print("测试重构后的代码")
print("=" * 60)

print("\n1. 测试导入 agent_tools...")
try:
    from agent.tools.agent_tools import (
        _is_safe_identifier,
        get_db_connection,
        get_chat_history_from_db,
        _generate_persona,
        generate_persona_from_db
    )
    print("[OK] 导入成功")
    
    print("\n2. 测试 _is_safe_identifier 函数...")
    test_cases = [
        ("talkrecord", True),
        ("studentId", True),
        ("content123", True),
        ("table; DROP", False),
        ("123table", True),
        ("table-name", False)
    ]
    all_passed = True
    for ident, expected in test_cases:
        result = _is_safe_identifier(ident)
        status = "[OK]" if result == expected else "[ERROR]"
        print(f"  {status} {ident}: {result} (期望: {expected})")
        if result != expected:
            all_passed = False
    if all_passed:
        print("[OK] 所有测试用例通过")
    
    print("\n3. 检查函数列表...")
    import agent.tools.agent_tools as at
    functions = [f for f in dir(at) if not f.startswith('_') and callable(getattr(at, f))]
    print(f"  公开函数: {functions}")
    
    print("\n" + "=" * 60)
    print("重构验证完成！")
    print("=" * 60)
    print("\n主要改进：")
    print("- 移除了历史遗留代码（天气、位置等无关工具）")
    print("- 统一了函数命名（get_chat_history_from_db）")
    print("- 消除了重复函数定义")
    print("- 导入语句统一放在文件顶部")
    print("- 添加了类型注解")
    print("- 区分了核心函数和@tool装饰的Agent工具函数")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
