"""基础功能测试 —— 验证环境搭建是否成功"""
import pytest


def test_addition():
    assert 1 + 1 == 2


def test_string_operation():
    assert "hello".upper() == "HELLO"


@pytest.mark.smoke
def test_env_setup():
    """验证测试环境是否正常"""
    assert True


def test_src_importable():
    """验证 src 模块可以正常导入（修复 pythonpath 后的验证）"""
    from src.llm_client import ask_llm
    assert callable(ask_llm)
