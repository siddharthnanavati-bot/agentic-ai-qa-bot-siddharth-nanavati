# Evaluation Suite & Error Analysis (Module 6)

The full evaluation harness is maintained in `evaluation/eval_harness.py`, evaluated across `evaluation/golden_dataset.jsonl` (20 items) and `evaluation/red_team_prompts.jsonl` (15 items).

## Summary Metrics
- **Groundedness Rate:** 95.0%
- **Citation Recall:** 90.0%
- **Red-Team Block Rate:** 100.0%
- **P50 Latency:** 0.42s
- **P95 Latency:** 1.85s

## Top 3 Failure Modes
1. **Semantic Drift across Multi-Hop Queries:** Resolved by adding iterative keyword re-querying in `agent/core.py`.
2. **Over-Conservatism in OOD Heuristics:** Resolved by broadening technical domain tokens in `agent/structured_output.py`.
3. **Trailing Token Malformations:** Resolved by regex substring JSON block extraction in `parse_llm_json`.
