import re
import os
from typing import Optional
from dotenv import load_dotenv
import requests

from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from utils.cache_manager import get_persona_cache
from utils.retry_utils import with_retry, llm_retry_config
from model.factory import chat_model

load_dotenv()

PROXY_API_URL = os.getenv("PROXY_API_URL", "")
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "")


def get_chat_history_from_db(participant_id: str) -> str:
    """
    通过数据库代理服务获取指定参与者的对话历史
    
    Args:
        participant_id: 参与者ID（学生ID）
    
    Returns:
        对话历史文本
    """
    try:
        if not PROXY_API_URL:
            return "错误：未配置数据库代理服务地址 (PROXY_API_URL)"
        
        headers = {}
        if PROXY_API_KEY:
            headers["X-Proxy-API-Key"] = PROXY_API_KEY
        
        payload = {
            "student_id": participant_id,
            "limit": 100
        }
        
        logger.info(f"[代理调用] 请求对话历史，学生ID: {participant_id}")
        
        response = requests.post(
            f"{PROXY_API_URL.rstrip('/')}/chat-history",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") != "success":
            return f"代理服务错误: {result.get('message', '未知错误')}"
        
        records = result.get("data", [])
        
        if not records:
            return "未找到历史会谈信息"
        
        chat_history = []
        for record in records:
            content = record.get("content", "")
            talk_time = record.get("created_time", "")
            chat_history.append(f"时间: {talk_time}\n内容: {content}")
        
        return "\n\n".join(chat_history)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[get_chat_history_from_db]代理服务调用失败: {str(e)}")
        return f"代理服务调用失败: {str(e)}"
    except Exception as e:
        logger.error(f"[get_chat_history_from_db]获取对话历史失败: {str(e)}")
        return f"获取对话历史失败: {str(e)}"


@with_retry(config=llm_retry_config)
def _generate_persona(chat_history: str, target_person: str = "对方", participant_id: Optional[str] = None) -> str:
    """
    根据对话记录分析指定人物的人物画像（简化版：不使用向量库）
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
        participant_id: 参与者ID（用于缓存，不使用向量库）
    
    Returns:
        人物画像描述
    """
    persona_prompt_path = get_abs_path("prompts/persona_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    prompt_template = PromptTemplate.from_template(persona_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    persona_result = chain.invoke({"chat_history": chat_history, "target_person": target_person})
    
    return persona_result


def generate_persona_from_db(participant_id: str, participant_name: Optional[str] = None) -> str:
    """
    根据数据库中的历史会谈信息生成人物画像（带缓存）
    
    Args:
        participant_id: 参与者ID
        participant_name: 参与者姓名（可选）
    
    Returns:
        人物画像描述
    """
    cache = get_persona_cache()
    cache_key = f"persona:{participant_id}"
    
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"[缓存] 人物画像命中缓存: {participant_id}")
        return cached_result
    
    chat_history = get_chat_history_from_db(participant_id)
    
    if "未找到" in chat_history or "失败" in chat_history:
        return chat_history
    
    target_person = participant_name if participant_name else f"ID为{participant_id}的用户"
    result = _generate_persona(chat_history, target_person, participant_id)
    
    cache.set(cache_key, result)
    logger.info(f"[缓存] 人物画像已缓存: {participant_id}")
    
    return result


@tool(description="从数据库中拉取历史会谈信息")
def get_chat_history(participant_id: str) -> str:
    """
    从数据库获取指定参与者的对话历史（Agent工具）
    """
    return get_chat_history_from_db(participant_id)


@tool(description="根据对话记录分析指定人物的人物画像")
def generate_persona_tool(chat_history: str, target_person: str = "对方") -> str:
    """
    根据对话记录分析指定人物的人物画像（Agent工具）
    """
    return _generate_persona(chat_history, target_person)


@tool(description="根据数据库中的历史会谈信息生成人物画像")
def generate_persona_from_db_tool(participant_id: str, participant_name: Optional[str] = None) -> str:
    """
    根据数据库中的历史会谈信息生成人物画像（Agent工具）
    """
    return generate_persona_from_db(participant_id, participant_name)


@with_retry(config=llm_retry_config)
def _generate_persona_simple(chat_history: str, target_person: str = "对方") -> str:
    """
    根据对话记录生成简化版人物画像
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
    
    Returns:
        简化版人物画像描述
    """
    persona_prompt_path = get_abs_path("prompts/persona_simple_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    prompt_template = PromptTemplate.from_template(persona_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    persona_result = chain.invoke({"chat_history": chat_history, "target_person": target_person})
    
    return persona_result


def generate_persona_simple_from_db(participant_id: str, participant_name: Optional[str] = None) -> str:
    """
    根据数据库中的历史会谈信息生成简化版人物画像
    
    Args:
        participant_id: 参与者ID
        participant_name: 参与者姓名（可选）
    
    Returns:
        简化版人物画像描述
    """
    chat_history = get_chat_history_from_db(participant_id)
    
    if "未找到" in chat_history or "失败" in chat_history:
        return chat_history
    
    target_person = participant_name if participant_name else f"ID为{participant_id}的用户"
    result = _generate_persona_simple(chat_history, target_person)
    
    return result


async def generate_persona_stream(chat_history: str, target_person: str = "对方"):
    """
    根据对话记录流式生成简化版人物画像
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
    
    Yields:
        人物画像片段
    """
    persona_prompt_path = get_abs_path("prompts/persona_simple_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    prompt_template = PromptTemplate.from_template(persona_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    async for chunk in chain.astream({"chat_history": chat_history, "target_person": target_person}):
        yield chunk


async def generate_persona_simple_from_db_stream(participant_id: str, participant_name: Optional[str] = None):
    """
    根据数据库中的历史会谈信息流式生成简化版人物画像
    
    Args:
        participant_id: 参与者ID
        participant_name: 参与者姓名（可选）
    
    Yields:
        人物画像片段
    """
    chat_history = get_chat_history_from_db(participant_id)
    
    if "未找到" in chat_history or "失败" in chat_history:
        yield chat_history
        return
    
    target_person = participant_name if participant_name else f"ID为{participant_id}的用户"
    
    async for chunk in generate_persona_stream(chat_history, target_person):
        yield chunk
