"""RAG 链路示例 —— 检索增强生成的简化实现

用于 DeepEval Faithfulness 测试的演示
"""
from src.llm_client import ask_llm


# 模拟知识库
KNOWLEDGE_BASE = {
    "腾讯": "腾讯控股有限公司，成立于1998年11月，创始人为马化腾、张志东等五人。总部位于深圳。",
    "阿里巴巴": "阿里巴巴集团，成立于1999年，由马云等18人在杭州创立。是全球最大的电子商务公司之一。",
    "字节跳动": "字节跳动，成立于2012年，总部位于北京。旗下产品包括抖音、今日头条等。",
}


def retrieve_context(query: str) -> list[str]:
    """从知识库检索相关上下文（简化版：关键词匹配）"""
    contexts = []
    for key, doc in KNOWLEDGE_BASE.items():
        if key in query:
            contexts.append(doc)
    return contexts


def rag_answer(question: str) -> tuple[str, list[str]]:
    """RAG 链路：检索 + 生成

    Returns:
        (answer, retrieval_context)
    """
    contexts = retrieve_context(question)
    context_text = "\n".join(contexts) if contexts else "无相关上下文"

    system_prompt = (
        "你是一个问答助手。请根据以下上下文回答问题，"
        "如果上下文中没有答案，请说'我不知道'。\n\n"
        f"上下文：\n{context_text}"
    )

    answer = ask_llm(question, system_prompt=system_prompt, use_cache=True)
    return answer, contexts
