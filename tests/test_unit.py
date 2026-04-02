#!/usr/bin/env python3
"""
单元测试 - 核心逻辑测试
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock


class TestSQLInjection(unittest.TestCase):
    """测试SQL注入防护"""
    
    def test_is_safe_identifier_valid(self):
        """测试安全的SQL标识符"""
        from agent.tools.agent_tools import _is_safe_identifier
        
        valid_cases = [
            "talkrecord",
            "studentId",
            "content",
            "createTime",
            "table123",
            "my_table",
            "MY_TABLE",
            "t"
        ]
        
        for ident in valid_cases:
            with self.subTest(ident=ident):
                self.assertTrue(_is_safe_identifier(ident))
    
    def test_is_safe_identifier_invalid(self):
        """测试不安全的SQL标识符"""
        from agent.tools.agent_tools import _is_safe_identifier
        
        invalid_cases = [
            "table; DROP",
            "table-name",
            "table;SELECT",
            "student' OR '1'='1",
            "table/*comment*/",
            "`table`",
            "",
            None
        ]
        
        for ident in invalid_cases:
            with self.subTest(ident=ident):
                self.assertFalse(_is_safe_identifier(ident))


class TestCacheManager(unittest.TestCase):
    """测试缓存管理器"""
    
    def test_cache_set_get(self):
        """测试缓存设置和获取"""
        from utils.cache_manager import TTLCache
        
        cache = TTLCache(max_size=10, ttl_seconds=3600)
        
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        from utils.cache_manager import TTLCache
        
        cache = TTLCache(max_size=10, ttl_seconds=3600)
        self.assertIsNone(cache.get("nonexistent"))
    
    def test_cache_delete(self):
        """测试缓存删除"""
        from utils.cache_manager import TTLCache
        
        cache = TTLCache(max_size=10, ttl_seconds=3600)
        cache.set("key1", "value1")
        cache.delete("key1")
        self.assertIsNone(cache.get("key1"))
    
    def test_cache_lru_eviction(self):
        """测试LRU淘汰策略"""
        from utils.cache_manager import TTLCache
        
        cache = TTLCache(max_size=3, ttl_seconds=3600)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # 访问key1，使其成为最新
        cache.get("key1")
        
        # 添加key4，应该淘汰key2（最旧）
        cache.set("key4", "value4")
        
        self.assertIsNone(cache.get("key2"))
        self.assertIsNotNone(cache.get("key1"))
    
    def test_cache_clear(self):
        """测试清空缓存"""
        from utils.cache_manager import TTLCache
        
        cache = TTLCache(max_size=10, ttl_seconds=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        self.assertEqual(cache.get_stats()["size"], 0)


class TestRetryUtils(unittest.TestCase):
    """测试重试工具"""
    
    def test_retry_success(self):
        """测试重试成功"""
        from utils.retry_utils import with_retry, RetryConfig
        
        call_count = [0]
        
        @with_retry(config=RetryConfig(max_retries=2, initial_delay=0.1))
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Temporary error")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 2)
    
    def test_retry_exhausted(self):
        """测试重试耗尽"""
        from utils.retry_utils import with_retry, RetryConfig
        
        call_count = [0]
        
        @with_retry(config=RetryConfig(max_retries=2, initial_delay=0.1))
        def always_fails():
            call_count[0] += 1
            raise Exception("Always fails")
        
        with self.assertRaises(Exception):
            always_fails()
        
        self.assertEqual(call_count[0], 3)  # 1次初始 + 2次重试


class TestInputValidation(unittest.TestCase):
    """测试输入验证"""
    
    def test_persona_request_valid(self):
        """测试有效的参与者ID"""
        from pydantic import ValidationError
        from api import PersonaRequest
        
        valid_ids = [
            "S2023003",
            "12345",
            "student-123",
            "a" * 100
        ]
        
        for pid in valid_ids:
            with self.subTest(pid=pid):
                req = PersonaRequest(participant_id=pid)
                self.assertEqual(req.participant_id, pid.strip())
    
    def test_persona_request_invalid(self):
        """测试无效的参与者ID"""
        from pydantic import ValidationError
        from api import PersonaRequest
        
        invalid_cases = [
            "",
            "   ",
            "a" * 101
        ]
        
        for pid in invalid_cases:
            with self.subTest(pid=pid):
                with self.assertRaises(ValidationError):
                    PersonaRequest(participant_id=pid)


if __name__ == "__main__":
    print("=" * 60)
    print("运行单元测试")
    print("=" * 60)
    
    unittest.main(verbosity=2)
