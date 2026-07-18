"""tests/conftest.py —— pytest 全局 fixture 和测试数据加载"""
import csv
import os
import pytest
import yaml
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_qa_pairs():
    data_file = DATA_DIR / "qa_pairs.csv"
    with open(data_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_injection_cases():
    data_file = DATA_DIR / "injection_cases.yaml"
    with open(data_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def qa_pairs():
    return load_qa_pairs()


@pytest.fixture
def injection_cases():
    return load_injection_cases()


def pytest_runtest_setup(item):
    if os.getenv("SKIP_LLM_CALLS") == "true":
        if "eval" in item.keywords or "safety" in item.keywords:
            pytest.skip("跳过 LLM 调用测试（CI 成本控制）")


def get_judge_model():
    base_url = os.getenv("OPENAI_BASE_URL", "")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_name = os.getenv("LLM_MODEL", "deepseek-chat")

    if api_key and "deepseek" in base_url:
        from deepeval.models.llms.deepseek_model import DeepSeekModel
        return DeepSeekModel(model=model_name, api_key=api_key)
    return None


