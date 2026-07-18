"""根目录 conftest.py —— 全局配置：自动创建 reports 目录"""
import os
from pathlib import Path

# 确保报告输出目录存在（修复 pytest-html 报错）
reports_dir = Path(__file__).parent / "reports"
reports_dir.mkdir(exist_ok=True)
