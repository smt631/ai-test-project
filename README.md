# AI Test Project

Python + pytest AI 自动化测试项目。

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实 API Key

# 4. 运行测试
pytest                          # 全部测试
pytest -m smoke -v              # 只跑冒烟测试
pytest -m "not eval" -v         # 跳过 LLM 评测（不调 API）
```

## 项目结构

```
ai-test-project/
├── src/                          # 被测代码
│   ├── llm_client.py             # LLM API 封装（含 retry + 缓存）
│   └── rag_pipeline.py           # RAG 链路
├── tests/                        # 测试代码
│   ├── conftest.py               # fixture + 数据加载
│   ├── test_basic.py             # 基础功能测试
│   ├── test_llm_eval.py          # LLM 评测测试
│   ├── test_safety.py            # 安全测试
│   └── data/                     # 测试数据
├── conftest.py                   # 根配置（自动创建 reports/）
├── pytest.ini                    # pytest 配置
├── .coveragerc                   # 覆盖率配置
├── .github/workflows/test.yml    # CI 配置
└── requirements.txt
```
