"""LLM 评测测试 —— DeepEval + 参数化 + Mock"""
import pytest
from src.llm_client import ask_llm
from tests.conftest import load_qa_pairs, get_judge_model

try:
    from deepeval import assert_test
    from deepeval.test_case import LLMTestCase
    from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False


@pytest.fixture
def faithfulness_metric():
    if not DEEPEVAL_AVAILABLE:
        pytest.skip("DeepEval 未安装")
    model = get_judge_model()
    kwargs = {"threshold": 0.7}
    if model:
        kwargs["model"] = model
    return FaithfulnessMetric(**kwargs)


@pytest.fixture
def relevancy_metric():
    if not DEEPEVAL_AVAILABLE:
        pytest.skip("DeepEval 未安装")
    model = get_judge_model()
    kwargs = {"threshold": 0.7}
    if model:
        kwargs["model"] = model
    return AnswerRelevancyMetric(**kwargs)


@pytest.mark.parametrize("question,expected_keyword", [
    ("腾讯的创始人是谁？", "马化腾"),
    ("阿里巴巴成立于哪一年？", "1999"),
    ("字节跳动的总部在哪？", "北京"),
])
def test_llm_basic_answer_mock(question, expected_keyword, monkeypatch):
    def fake_ask_llm(q, **kwargs):
        mock_answers = {
            "腾讯的创始人是谁？": "腾讯由马化腾等人创立。",
            "阿里巴巴成立于哪一年？": "阿里巴巴成立于1999年。",
            "字节跳动的总部在哪？": "字节跳动总部位于北京。",
        }
        return mock_answers.get(q, "我不知道")

    monkeypatch.setattr("tests.test_llm_eval.ask_llm", fake_ask_llm)
    response = ask_llm(question)
    assert expected_keyword in response, \
        f"回答中应包含 '{expected_keyword}'，实际返回：{response}"


@pytest.mark.parametrize("case", load_qa_pairs(), ids=lambda c: c["question"][:10])
def test_qa_from_csv_mock(case, monkeypatch):
    def fake_ask_llm(q, **kwargs):
        mock_map = {
            "腾讯的创始人是谁？": "腾讯由马化腾等人于1998年创立。",
            "阿里巴巴成立于哪一年？": "阿里巴巴成立于1999年。",
            "字节跳动的总部在哪？": "字节跳动总部位于北京。",
            "光速是多少？": "光速约为299792458米每秒。",
            "水的化学式是什么？": "水的化学式是H2O。",
        }
        return mock_map.get(q, "我不知道")

    monkeypatch.setattr("tests.test_llm_eval.ask_llm", fake_ask_llm)
    response = ask_llm(case["question"])
    assert case["expected_keyword"] in response, \
        f"[{case['category']}] 期望包含 '{case['expected_keyword']}'，实际：{response}"


@pytest.mark.eval
def test_faithfulness_rag(faithfulness_metric):
    test_case = LLMTestCase(
        input="腾讯是哪一年成立的？",
        actual_output="腾讯由马化腾等人于1998年11月创立。",
        retrieval_context=[
            "腾讯控股有限公司，成立于1998年11月，创始人为马化腾、张志东等五人。"
        ],
    )
    assert_test(test_case, [faithfulness_metric])


@pytest.mark.eval
def test_answer_relevancy(relevancy_metric):
    test_case = LLMTestCase(
        input="腾讯的创始人是谁？",
        actual_output="腾讯由马化腾等人于1998年创立。",
        expected_output="腾讯的创始人是马化腾。",
    )
    assert_test(test_case, [relevancy_metric])


@pytest.mark.parametrize("case", load_qa_pairs(), ids=lambda c: c["question"][:10])
@pytest.mark.eval
def test_batch_eval(case, relevancy_metric):
    response = ask_llm(case["question"], use_cache=True)
    test_case = LLMTestCase(
        input=case["question"],
        actual_output=response,
        expected_output=case["expected_output"],
    )
    assert_test(test_case, [relevancy_metric])

