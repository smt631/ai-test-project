"""LLM 客户端封装 —— 统一调用入口，方便 Mock 和切换模型

修正点：
1. 增加 retry + 指数退避（处理超时、限流）
2. 增加异常捕获（网络错误、API 错误）
3. 增加 API 响应缓存（降低评测成本）
"""
import os
import time
import json
import hashlib
from pathlib import Path
from functools import lru_cache
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

load_dotenv()

# 单例 client（避免重复初始化）
_client = None

# 缓存目录
_CACHE_DIR = Path(__file__).parent.parent / ".cache"


def get_client():
    """获取 OpenAI 客户端单例"""
    global _client
    if _client is None:
        # 兼容 GitHub Secrets 的两种命名：优先 LLM_API_KEY，回退 OPENAI_API_KEY
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30,  # 30 秒超时
        )
    return _client


def _get_cache_key(question: str, model: str, system_prompt: str = None) -> str:
    """生成缓存键"""
    content = f"{question}|{model}|{system_prompt or ''}"
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def _load_from_cache(cache_key: str) -> str | None:
    """从文件缓存加载"""
    cache_file = _CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        return data.get("response")
    return None


def _save_to_cache(cache_key: str, response: str):
    """保存到文件缓存"""
    _CACHE_DIR.mkdir(exist_ok=True)
    cache_file = _CACHE_DIR / f"{cache_key}.json"
    cache_file.write_text(
        json.dumps({"response": response}, ensure_ascii=False),
        encoding="utf-8",
    )


def ask_llm(
    question: str,
    system_prompt: str = None,
    model: str = None,
    use_cache: bool = False,
    max_retries: int = 3,
) -> str:
    """调用 LLM 并返回回答文本

    Args:
        question: 用户问题
        system_prompt: 系统提示词（可选）
        model: 模型名称（可选，默认从环境变量读取）
        use_cache: 是否使用文件缓存（评测时建议开启，省钱）
        max_retries: 最大重试次数

    Returns:
        LLM 回答文本

    Raises:
        RuntimeError: 所有重试失败后抛出
    """
    model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    # 检查缓存
    if use_cache:
        cache_key = _get_cache_key(question, model, system_prompt)
        cached = _load_from_cache(cache_key)
        if cached is not None:
            return cached

    client = get_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,  # 测试时固定温度，保证可复现
            )
            result = response.choices[0].message.content

            # 保存缓存
            if use_cache:
                _save_to_cache(cache_key, result)

            return result

        except (APITimeoutError, RateLimitError) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避：1s, 2s, 4s
                print(f"  [retry] 第 {attempt + 1} 次失败 ({type(e).__name__})，"
                      f"{wait_time}s 后重试...")
                time.sleep(wait_time)

        except APIConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

        except APIError as e:
            # 非 retriable 的 API 错误，直接抛出
            raise RuntimeError(f"LLM API 调用失败: {e}") from e

    raise RuntimeError(
        f"LLM API 调用失败（重试 {max_retries} 次后仍失败）: {last_error}"
    )
