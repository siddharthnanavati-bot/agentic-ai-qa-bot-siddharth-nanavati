"""
Module: structured_output.py
Purpose: Pydantic models for structured LLM responses, plus validation and
         out-of-distribution (OOD) detection.
Evidence: Module 3 — Foundation Models and Structured Outputs.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional

from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class Source(BaseModel):
    """A single cited source backing a claim in the answer."""

    doc_id: str
    title: str
    snippet: str
    score: float  # retrieval / relevance score, 0.0–1.0

    @field_validator("score")
    @classmethod
    def score_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"score must be in [0, 1], got {v}")
        return round(v, 4)

    @field_validator("snippet")
    @classmethod
    def snippet_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("snippet must not be empty")
        return v


class AnswerModel(BaseModel):
    """
    The structured answer returned by the agent for every query.
    """

    answer: str
    confidence: float          # 0.0 (low) → 1.0 (high)
    sources: list[Source]
    reasoning_steps: list[str]  # chain-of-thought trace
    is_grounded: bool           # True when at least one source was used
    out_of_domain: bool = False # True when query falls outside corpus scope

    @field_validator("confidence")
    @classmethod
    def confidence_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {v}")
        return round(v, 4)

    @model_validator(mode="after")
    def grounded_requires_sources(self) -> "AnswerModel":
        if self.is_grounded and not self.sources:
            raise ValueError(
                "is_grounded=True but no sources provided — "
                "either add sources or set is_grounded=False"
            )
        return self


class SourcedAnswer(AnswerModel):
    """Alias kept for backward-compatibility."""
    pass


# ---------------------------------------------------------------------------
# Parser + OOD detection
# ---------------------------------------------------------------------------

# Known domains this agent covers (used for OOD check)
KNOWN_DOMAINS = frozenset(
    [
        "machine learning",
        "software testing",
        "agentic ai",
        "python",
        "observability",
        "evaluation",
        "safety",
        "llm",
        "language model",
        "retrieval",
        "rag",
        "orchestration",
    ]
)

# Trigger phrases that suggest out-of-scope queries
OOD_TRIGGERS = [
    r"\b(recipe|cooking|chef|food)\b",
    r"\b(stock|forex|crypto|invest)\b",
    r"\b(diagnos|medical|symptom|disease)\b",
    r"\b(legal advice|lawsuit|attorney)\b",
]


def is_out_of_domain(query: str) -> bool:
    """
    Heuristic OOD check: returns True if the query appears to be outside
    the corpus domain.  Used to flag answers before returning to the user.
    """
    q_lower = query.lower()
    for pattern in OOD_TRIGGERS:
        if re.search(pattern, q_lower):
            return True
    # If none of the known domain keywords appear, treat as OOD
    if not any(kw in q_lower for kw in KNOWN_DOMAINS):
        return True
    return False


def parse_llm_json(raw: str) -> dict[str, Any]:
    """
    Extract the first JSON object from an LLM response string.
    Handles markdown code-fences (```json … ```) gracefully.
    Raises ValueError on malformed JSON.
    """
    # Strip markdown fences if present
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if fenced:
        raw = fenced.group(1)
    # Find the outermost JSON object
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in LLM output:\n{raw[:300]}")
    candidate = raw[start:end]
    return json.loads(candidate)


def build_answer(raw_llm_output: str, query: str) -> AnswerModel:
    """
    Parse raw LLM text into an AnswerModel.
    Sets out_of_domain=True when the OOD heuristic fires.
    Raises ValueError / ValidationError on malformed output.
    """
    data = parse_llm_json(raw_llm_output)
    model = AnswerModel(**data)
    if is_out_of_domain(query):
        object.__setattr__(model, "out_of_domain", True)
    return model


# ---------------------------------------------------------------------------
# Schema export (for the LLM system prompt)
# ---------------------------------------------------------------------------

ANSWER_JSON_SCHEMA = AnswerModel.model_json_schema()

STRUCTURED_OUTPUT_SYSTEM_PROMPT = f"""
You are a grounded research assistant. Answer ONLY using evidence from the
provided corpus. Return your answer as a single JSON object matching this
schema (no markdown, no prose before or after the JSON):

{json.dumps(ANSWER_JSON_SCHEMA, indent=2)}

Rules:
- confidence: how certain you are, 0.0–1.0.
- is_grounded: true only if you cite at least one source.
- out_of_domain: true if the question cannot be answered from the corpus.
- reasoning_steps: list each reasoning step you took.
- Do NOT fabricate sources.
""".strip()
