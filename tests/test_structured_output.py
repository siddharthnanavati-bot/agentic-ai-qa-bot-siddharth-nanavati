import pytest
from pydantic import ValidationError
from agent.structured_output import AnswerModel, build_answer, is_out_of_domain


def test_valid_structured_answer():
    raw_json = """
    {
      "answer": "Determinism prevents flaky test suites.",
      "confidence": 0.95,
      "sources": [
        {
          "doc_id": "doc_01",
          "title": "Agentic Testing",
          "snippet": "Enforces seed pinning",
          "score": 0.88
        }
      ],
      "reasoning_steps": ["Retrieved doc_01", "Extracted evidence"],
      "is_grounded": true,
      "out_of_domain": false
    }
    """
    model = build_answer(raw_json, "How does determinism help?")
    assert model.confidence == 0.95
    assert model.is_grounded is True
    assert len(model.sources) == 1


def test_grounded_requires_sources_validation():
    with pytest.raises(ValidationError):
        AnswerModel(
            answer="Fake claim without sources.",
            confidence=0.9,
            sources=[],
            reasoning_steps=[],
            is_grounded=True,
        )


def test_ood_detection():
    assert is_out_of_domain("Can you give me a recipe for chocolate cake?") is True
    assert is_out_of_domain("What are best practices in machine learning testing?") is False
