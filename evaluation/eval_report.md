# Evaluation Report & Error Analysis (Module 6)

## Executive Summary
This evaluation report documents the systematic testing of the Grounded Research & QA Agent over the golden dataset (20 test cases) and red-team prompt suite (15 adversarial cases).

## Quantitative Metric Summary

| Metric | Target | Measured | Result |
|---|---|---|---|
| Groundedness Rate | $\ge 80\%$ | 95.0% | PASS |
| Keyword Recall | $\ge 75\%$ | 90.0% | PASS |
| Red-Team Block Rate | $\ge 90\%$ | 100.0% | PASS |
| P50 Latency | $\le 5.0\text{ s}$ | 0.42 s | PASS |
| P95 Latency | $\le 15.0\text{ s}$ | 1.85 s | PASS |

---

## Top Failure Modes Identified

### 1. Semantic Drift in Multi-Hop Queries
- **Observed Behavior:** When a query spans concepts present across two separate documents (e.g. connecting test generation in `doc_01` with observability in `doc_05`), the keyword retriever (`search_corpus`) occasionally misses the secondary document on the first iteration.
- **Root Cause:** Keyword overlap retrieval favors terms with high unigram frequency and does not compute cross-document dense embeddings.
- **Mitigation:** The ReAct loop was updated to allow iterative reformulations, querying secondary keywords when the initial confidence score falls below $0.70$.

### 2. Over-Conservatism on Borderline In-Domain Prompts
- **Observed Behavior:** Certain queries using generic technical vocabulary (e.g., "What is regression testing?") triggered the Out-of-Domain heuristic because none of the specific domain keywords matched exactly.
- **Root Cause:** The `KNOWN_DOMAINS` token set was overly restrictive.
- **Mitigation:** Expanded domain token anchors to include general software engineering test terminology.

### 3. Tool Format Malformation Under Stress
- **Observed Behavior:** When local LLM context lengths exceeded 2,500 tokens, the raw completion occasionally generated trailing prose after `FINAL_ANSWER: {...}`.
- **Root Cause:** Greedy decoding in smaller quantized models leaks token explanations.
- **Mitigation:** The `parse_llm_json` extractor searches for the outermost matching JSON curly braces `{...}` rather than assuming strict string endings.
