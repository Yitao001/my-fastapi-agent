import os
import re
from datetime import datetime
from typing import Optional, List, Tuple

from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import mysql.connector
from mysql.connector import Error

from rag.rag_service import RagSummarizeService
from rag.vector_store import VectorStoreService
from utils.config_handler import db_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from utils.db_pool import get_db_connection_from_pool
from utils.cache_manager import get_persona_cache
from utils.retry_utils import with_retry, llm_retry_config
from model.factory import chat_model


def _is_safe_identifier(identifier: str) -> bool:
    """
    验证SQL标识符是否安全，防止SQL注入
    只允许字母、数字、下划线
    """
    return bool(re.match(r'^[A-Za-z0-9_]+$', identifier))


def get_db_connection() -> mysql.connector.connection.MySQLConnection:
    """
    获取数据库连接（使用连接池）
    
    Returns:
        mysql.connector.connection.MySQLConnection: 数据库连接对象
    """
    try:
        return get_db_connection_from_pool()
    except Error as e:
        logger.error(f"[get_db_connection]MySQL连接失败：{str(e)}")
        raise e


def get_chat_history_from_db(participant_id: str) -> str:
    """
    从数据库获取指定参与者的对话历史
    
    Args:
        participant_id: 参与者ID（学生ID）
    
    Returns:
        对话历史文本
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        table_config = db_conf.get("table_structure", {})
        table_name = table_config.get("table_name", "talk_record")
        fields = table_config.get("fields", {})
        query_limit = table_config.get("query_limit", 100)
        
        student_id_field = fields.get("student_id", "student_id")
        content_field = fields.get("content", "content")
        created_time_field = fields.get("created_time", "created_time")
        
        if not all(_is_safe_identifier(ident) for ident in [table_name, student_id_field, content_field, created_time_field]):
            logger.error("[get_chat_history_from_db]检测到不安全的SQL标识符")
            return "数据库配置错误"
        
        try:
            query_limit = int(query_limit)
            if query_limit < 1 or query_limit > 1000:
                query_limit = 100
        except (ValueError, TypeError):
            query_limit = 100
        
        query = f"""
        SELECT {content_field}, {created_time_field} 
        FROM {table_name} 
        WHERE {student_id_field} = %s 
        ORDER BY {created_time_field} DESC 
        LIMIT {query_limit}
        """
        
        cursor.execute(query, (participant_id,))
        results = cursor.fetchall()
        
        if not results:
            cursor.close()
            conn.close()
            return "未找到历史会谈信息"
        
        chat_history = []
        for row in results:
            content, talk_time = row
            chat_history.append(f"时间: {talk_time}\n内容: {content}")
        
        cursor.close()
        conn.close()
        
        return "\n\n".join(chat_history)
    except Exception as e:
        logger.error(f"[get_chat_history_from_db]获取对话历史失败: {str(e)}")
        return f"获取对话历史失败: {str(e)}"


@with_retry(config=llm_retry_config)
def _generate_persona(chat_history: str, target_person: str = "对方", participant_id: Optional[str] = None) -> str:
    """
    根据对话记录分析指定人物的人物画像
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
        participant_id: 参与者ID，用于存储和检索向量库
    
    Returns:
        人物画像描述
    """
    persona_prompt_path = get_abs_path("prompts/persona_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    rag_service = RagSummarizeService()
    vector_store = VectorStoreService()
    
    retrieval_query = f"{target_person}的人物画像分析，包括性格特征、核心问题和当前状态"
    context_docs = rag_service.retriever_docs(retrieval_query)
    
    context = ""
    counter = 0
    for doc in context_docs:
        counter += 1
        context += f"[参考资料{counter}]:{doc.page_content}\n"
    
    enhanced_prompt = persona_prompt + "\n\n# 参考资料\n" + context
    
    prompt_template = PromptTemplate.from_template(enhanced_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    persona_result = chain.invoke({"chat_history": chat_history, "target_person": target_person})
    
    if participant_id:
        doc_content = f"参与者ID: {participant_id}\n人物画像: {persona_result}\n谈话记录: {chat_history}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        document = Document(
            page_content=doc_content,
            metadata={
                "participant_id": participant_id,
                "type": "persona_analysis",
                "created_at": datetime.now().isoformat()
            }
        )
        
        try:
            vector_store.vector_store.add_documents([document])
            logger.info(f"[向量库] 参与者 {participant_id} 的人物画像已成功存入向量库")
        except Exception as e:
            logger.error(f"[向量库] 存入人物画像失败: {str(e)}")
    
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
