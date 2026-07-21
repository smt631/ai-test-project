# AI Test Project · LLM/RAG 自动化测试

> 用 pytest + DeepEval 为「大语言模型 / RAG 应用」构建的一套自动化测试方案，覆盖功能、评测与安全三类测试，并接入 GitHub Actions 实现 CI 自动跑测。

## 这个项目解决什么问题

LLM / RAG 应用的输出是**非确定性**的——同一个问题每次回答可能不同，无法用传统「精确匹配期望值」的方式断言对错。本项目用三套互补的策略解决：

1. **Mock 单元测试**：对 LLM 调用做打桩（monkeypatch），验证 RAG 链路、工具函数等**确定逻辑**，零成本、可离线、随时绿。
2. **LLM-as-a-Judge 评测**：用 DeepEval 的 Faithfulness（忠实度）、AnswerRelevancy（相关性）指标，让另一个模型当「裁判」给输出打分，用**阈值断言**替代脆弱的精确匹配。
3. **安全测试（Prompt Injection）**：验证应用能拦截恶意注入指令，防止被越权操控。

## 技术亮点

- **非确定性测试的断言范式**：放弃 `assert output == expected`，改用「语义指标 + 阈值」判定，贴合 LLM 应用真实评测方法。
- **分层成本控制**：通过 `SKIP_LLM_CALLS` 环境变量区分——日常 push 只跑 Mock 测试（不调 API、零花费）；发起 PR 才跑真实 LLM 评测，兼顾「CI 永远绿」与「真实验证」。
- **DeepSeek 作 Judge，降本增效**：DeepSeek 兼容 OpenAI SDK，直接复用 DeepEval 的 `GPTModel` 接口替换默认 OpenAI Judge，评测成本大幅降低。
- **安全左移**：Prompt Injection 用例以数据驱动（`injection_cases.yaml`）组织，新增攻击手法只需补数据，不改测试代码。
- **CI/CD 开箱即用**：GitHub Actions 自动拉代码、装依赖、跑全量测试，并上传测试报告与覆盖率报告作为构建产物。

## 项目结构

```
ai-test-project/
├── src/
│   ├── llm_client.py        # LLM API 封装（含 retry + 缓存）
│   └── rag_pipeline.py      # RAG 检索增强链路
├── tests/
│   ├── conftest.py         # fixture + 测试数据加载 + 跳过逻辑
│   ├── test_basic.py        # 基础功能测试（mock）
│   ├── test_llm_eval.py     # LLM 评测测试（DeepEval Faithfulness / AnswerRelevancy）
│   ├── test_safety.py       # Prompt Injection 安全测试（mock）
│   └── data/               # qa_pairs.csv / injection_cases.yaml
├── conftest.py              # 根配置（自动创建 reports/）
├── pytest.ini               # pytest 配置
├── .coveragerc             # 覆盖率配置
├── requirements.txt
├── .env.example            # 环境变量模板（真实 .env 不入库）
└── .github/workflows/test.yml   # CI 配置
```

## 快速开始

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（填入真实 API Key，参考 .env.example）
cp .env.example .env
# 编辑 .env：LLM_API_KEY / LLM_BASE_URL / LLM_MODEL

# 4. 运行测试
pytest                              # 全部测试
pytest -m "not eval and not safety" -v   # 只跑 Mock 测试（不调 API）
pytest -m eval -v                  # 只跑 LLM 评测
```

## 各测试测什么

| 测试文件 | 标记 | 是否调 API | 验证点 |
|----------|------|-----------|--------|
| `test_basic.py` | `smoke` | 否（mock） | RAG 链路返回结构、LLM 封装的 retry / 缓存逻辑 |
| `test_llm_eval.py` | `eval` | 是 | 输出忠实于上下文（Faithfulness）、回答相关（AnswerRelevancy） |
| `test_safety.py` | `safety` | 否（mock） | 恶意注入指令被拦截，不执行越权操作 |

## CI 状态

推送 `main` 或发起 PR 时，GitHub Actions 会自动运行全量测试，并上传 `test-report` 与 `coverage-report` 两个产物。

> 注：真实 LLM 评测需要在仓库 **Settings → Secrets** 中配置 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` / `OPENAI_API_KEY` / `OPENAI_BASE_URL`。
