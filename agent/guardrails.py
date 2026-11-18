"""
Module: guardrails.py
Purpose: Input and output safety filters (regex + semantic heuristics).
Evidence: Module 8 - Red Teaming and Adversarial Testing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class GuardrailResult:
    passed: bool
    rule_name: str
    reason: str = ""
    matched: str = ""


GuardrailRule = Callable[[str], GuardrailResult]


def _regex_check(
    text: str,
    patterns: list[str],
    rule_name: str,
    reason: str,
) -> GuardrailResult:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            return GuardrailResult(
                passed=False,
                rule_name=rule_name,
                reason=reason,
                matched=m.group(0)[:120],
            )
    return GuardrailResult(passed=True, rule_name=rule_name)


_PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(your\s+)?system\s+prompt",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(if\s+you\s+are\s+)?(an?)\s*(jailbroken|evil|dan|unrestricted)",
    r"bypass\s+(safety|filter|guardrail|restriction)",
    r"<\|.*?\|>",
    r"\[\[.*?override.*?\]\]",
]

_PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",
    r"\b4[0-9]{12}(?:[0-9]{3})?\b",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
]

_SENSITIVE_TOPICS = [
    r"\b(synthesize|manufacture).{0,30}(drug|explosive|weapon|poison)",
    r"\b(how\s+to\s+(make|build|create))\s+(bomb|malware|ransomware)",
    r"\b(child|minor).{0,20}(explicit|sexual|nude)",
]


def rule_no_prompt_injection(text: str) -> GuardrailResult:
    return _regex_check(
        text, _PROMPT_INJECTION_PATTERNS,
        "no_prompt_injection",
        "Prompt-injection attempt detected.",
    )


def rule_no_pii_input(text: str) -> GuardrailResult:
    return _regex_check(
        text, _PII_PATTERNS,
        "no_pii_input",
        "PII detected in input (SSN, card number, or email).",
    )


def rule_no_sensitive_topics(text: str) -> GuardrailResult:
    return _regex_check(
        text, _SENSITIVE_TOPICS,
        "no_sensitive_topics",
        "Query requests harmful or illegal content.",
    )


def rule_max_input_length(text: str, max_chars: int = 2000) -> GuardrailResult:
    if len(text) > max_chars:
        return GuardrailResult(
            passed=False,
            rule_name="max_input_length",
            reason=f"Input exceeds {max_chars} characters ({len(text)} received).",
        )
    return GuardrailResult(passed=True, rule_name="max_input_length")


_HALLUCINATION_SIGNALS = [
    r"as\s+of\s+my\s+knowledge\s+cutoff",
    r"I\s+don't\s+have\s+access\s+to\s+real.time",
    r"I\s+cannot\s+browse\s+the\s+internet",
    r"I\s+am\s+not\s+able\s+to\s+verify",
]


def rule_no_ungrounded_refusal(text: str) -> GuardrailResult:
    return _regex_check(
        text, _HALLUCINATION_SIGNALS,
        "no_ungrounded_refusal",
        "Output contains ungrounded knowledge disclaimers; force corpus retrieval.",
    )


def rule_no_pii_output(text: str) -> GuardrailResult:
    return _regex_check(
        text, _PII_PATTERNS,
        "no_pii_output",
        "PII detected in output - scrubbing required before delivery.",
    )


@dataclass
class GuardrailPipeline:
    input_rules: list[GuardrailRule] = field(default_factory=list)
    output_rules: list[GuardrailRule] = field(default_factory=list)

    @classmethod
    def default(cls) -> "GuardrailPipeline":
        return cls(
            input_rules=[
                rule_no_prompt_injection,
                rule_no_pii_input,
                rule_no_sensitive_topics,
                rule_max_input_length,
            ],
            output_rules=[
                rule_no_ungrounded_refusal,
                rule_no_pii_output,
            ],
        )

    def check_input(self, text: str) -> GuardrailResult:
        for rule in self.input_rules:
            result = rule(text)
            if not result.passed:
                return result
        return GuardrailResult(passed=True, rule_name="all_input_rules")

    def check_output(self, text: str) -> GuardrailResult:
        for rule in self.output_rules:
            result = rule(text)
            if not result.passed:
                return result
        return GuardrailResult(passed=True, rule_name="all_output_rules")
