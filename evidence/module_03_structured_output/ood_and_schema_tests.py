"""
Tests Catching Malformed and Out-of-Distribution Responses (Module 3)
"""
import pytest
from pydantic import ValidationError
from agent.structured_output import build_answer, AnswerModel, is_out_of_domain


def test_malformed_json_raises_value_error():
    malformed_raw = "THOUGHT: I have no json here."
    with pytest.raises(ValueError, match="No JSON object found"):
        build_answer(malformed_raw, "query")


def test_missing_required_fields_raises_validation_error():
    incomplete_json = '{"answer": "Incomplete data"}'
    with pytest.raises(ValidationError):
        build_answer(incomplete_json, "query")


def test_confidence_out_of_bounds_caught():
    out_of_bounds = """
    {
      "answer": "Test",
      "confidence": 1.5,
      "sources": [],
      "reasoning_steps": [],
      "is_grounded": false
    }
    """
    with pytest.raises(ValidationError, match="confidence must be in"):
        build_answer(out_of_bounds, "query")


def test_out_of_distribution_query_flagged():
    ood_query = "What is the best recipe for baking chocolate cupcakes?"
    valid_json = """
    {
      "answer": "Cupcakes require flour, sugar, and cocoa.",
      "confidence": 0.9,
      "sources": [],
      "reasoning_steps": ["Used general recipe"],
      "is_grounded": false
    }
    """
    model = build_answer(valid_json, ood_query)
    assert model.out_of_domain is True
