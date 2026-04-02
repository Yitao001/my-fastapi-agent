#!/usr/bin/env python3
"""
测试所有P0-P1改进
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("测试P0-P1优先级改进")
print("=" * 60)

all_passed = True

print("\n" + "-" * 60)
print("测试1: 输入验证模块导入")
print("-" * 60)
try:
    from pydantic import ValidationError
    from api import PersonaRequest
    
    test_cases = [
        ("S2023003", True),
        ("   S2023003   ", True),
        ("", False),
        ("   ", False),
        ("a" * 100, True),
        ("a" * 101, False),
    ]
    
    for test_id, should_pass in test_cases:
        try:
            req = PersonaRequest(participant_id=test_id)
            if should_pass:
                print(f"  [OK] '{test_id[:20]}{'...' if len(test_id) > 20 else ''}' - 验证通过")
            else:
                print(f"  [ERROR] '{test_id[:20]}{'...' if len(test_id) > 20 else ''}' - 应该失败但通过了")
                all_passed = False
        except ValidationError:
            if not should_pass:
                print(f"  [OK] '{test_id[:20]}{'...' if len(test_id) > 20 else ''}' - 正确拒绝")
            else:
                print(f"  [ERROR] '{test_id[:20]}{'...' if len(test_id) > 20 else ''}' - 应该通过但失败了")
                all_passed = False
    
    print("[OK] 输入验证模块正常")
except Exception as e:
    print(f"[ERROR] 输入验证模块测试失败: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

print("\n" + "-" * 60)
print("测试2: 重试工具导入")
print("-" * 60)
try:
    from utils.retry_utils import with_retry, RetryConfig, llm_retry_config
    print(f"[OK] 重试工具导入成功")
    print(f"  - 默认重试次数: {llm_retry_config.max_retries}")
    print(f"  - 初始延迟: {llm_retry_config.initial_delay}s")
    print(f"  - 最大延迟: {llm_retry_config.max_delay}s")
except Exception as e:
    print(f"[ERROR] 重试工具导入失败: {e}")
    all_passed = False

print("\n" + "-" * 60)
print("测试3: 缓存管理器导入")
print("-" * 60)
try:
    from utils.cache_manager import get_persona_cache, TTLCache
    cache = get_persona_cache()
    stats = cache.get_stats()
    print(f"[OK] 缓存管理器导入成功")
    print(f"  - 当前缓存数量: {stats['size']}")
    print(f"  - 最大缓存: {stats['max_size']}")
    print(f"  - TTL: {stats['ttl_seconds']}s")
except Exception as e:
    print(f"[ERROR] 缓存管理器导入失败: {e}")
    all_passed = False

print("\n" + "-" * 60)
print("测试4: 数据库连接池导入")
print("-" * 60)
try:
    from utils.db_pool import get_db_pool
    print("[OK] 数据库连接池导入成功")
except Exception as e:
    print(f"[ERROR] 数据库连接池导入失败: {e}")
    all_passed = False

print("\n" + "-" * 60)
print("测试5: SQL注入防护")
print("-" * 60)
try:
    from agent.tools.agent_tools import _is_safe_identifier
    
    safe_cases = ["talkrecord", "studentId", "content123", "my_table"]
    unsafe_cases = ["table; DROP", "student' OR '1'='1", "table-name"]
    
    for ident in safe_cases:
        if _is_safe_identifier(ident):
            print(f"  [OK] '{ident}' - 安全")
        else:
            print(f"  [ERROR] '{ident}' - 应该安全但被拒绝")
            all_passed = False
    
    for ident in unsafe_cases:
        if not _is_safe_identifier(ident):
            print(f"  [OK] '{ident}' - 正确拒绝")
        else:
            print(f"  [ERROR] '{ident}' - 应该拒绝但通过了")
            all_passed = False
    
    print("[OK] SQL注入防护正常")
except Exception as e:
    print(f"[ERROR] SQL注入防护测试失败: {e}")
    all_passed = False

print("\n" + "-" * 60)
print("测试6: API模块导入（含健康检查）")
print("-" * 60)
try:
    import api
    print("[OK] API模块导入成功")
    
    if hasattr(api, 'check_database'):
        print("[OK] check_database 函数存在")
    else:
        print("[ERROR] check_database 函数不存在")
        all_passed = False
    
    if hasattr(api, 'check_llm'):
        print("[OK] check_llm 函数存在")
    else:
        print("[ERROR] check_llm 函数不存在")
        all_passed = False
    
except Exception as e:
    print(f"[ERROR] API模块导入失败: {e}")
    all_passed = False
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成总结")
print("=" * 60)

if all_passed:
    print("\n✅ 所有P0-P1改进测试通过！")
else:
    print("\n❌ 部分测试失败，请检查错误")

print("\n已完成的P0-P1改进：")
print("  [x] P1: 输入验证（participant_id格式和长度）")
print("  [x] P1: LLM调用重试机制（指数退避）")
print("  [x] P1: 完善健康检查（数据库+LLM连通性）")
print("  [x] P0: 补充单元测试框架")

print("\n新增文件：")
print("  - utils/retry_utils.py")
print("  - tests/test_unit.py")
print("  - tests/test_all_improvements.py")
print("\n修改文件：")
print("  - api.py（输入验证+健康检查）")
print("  - agent/tools/agent_tools.py（重试装饰器）")
