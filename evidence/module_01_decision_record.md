# Architectural Decision Record (ADR 001): Verifying Non-Deterministic Agent Systems

**Status:** Accepted  
**Date:** 2026-11-18  
**Author:** TAE Candidate  
**Context:** Sprint 0, Decision and Setup (Module 1)  

---

## The Question
> *How do you verify a system whose answers vary from run to run?*

## Decision
We verify the system through a multi-tiered validation architecture combining:
1. **Syntactic & Structural Invariants:** All agent responses must conform to a deterministic Pydantic schema (`AnswerModel`). Field presence, data types, and boundary values ($0.0 \le \text{confidence} \le 1.0$) are non-negotiable invariants.
2. **Groundedness Verification (Semantic Faithfulness):** Instead of exact string matching, we assert that claims made in the answer can be directly aligned with extracted corpus snippet spans. An answer is valid if and only if $\text{overlap}(\text{claims}, \text{source}) > \tau$.
3. **Statistical Acceptance Bands (Distributional Testing):** For non-deterministic multi-step outputs, benchmarks are executed over repeated trials ($N=5$). We assert against statistical thresholds:
   - Groundedness Rate $\ge 80\%$
   - Recall on critical facts $\ge 75\%$
   - 95% confidence intervals to distinguish true regressions from model variance.
4. **Behavioral Metamorphic Relations:** Testing invariance across prompt permutations (e.g., rephrasing the same query must not change the retrieved document set or trigger unexpected tool calls).

## Alternatives Considered & Rejected
- **Strict Golden String Assertions:** Rejected due to high fragility and 90%+ false alarms caused by superficial phrasing changes.
- **Pure Manual Spot Checking:** Rejected due to zero regression safety in continuous integration.
