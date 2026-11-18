# SYSTEM.md — Grounded Research & QA Agent

**Submission:** TAE Track Capstone Peer Review  
**Commit Reference:** `b6143fe` (`tag: v1.0.0-peer-review`)  
**Target Environment:** Local laptop (zero cloud spend fallback)  
**Evidence Index:** [`evidence/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence)

---

### 1. What the Agent Does
The Grounded Research & QA Agent is a fully local, tool-augmented reasoning system that answers complex technical questions strictly using verified documents from an underlying knowledge corpus. It generates structured, schema-validated JSON responses accompanied by verifiable citations, confidence scores, and chain-of-thought traces while rejecting out-of-domain prompts.

---

### 2. Architecture Chosen and Alternatives Rejected
- **Architecture Chosen:** ReAct (Reason + Act) loop paired with deterministic Pydantic schema validation, local Ollama execution (`llama3`), and pre/post-execution regex and AST guardrails.
- **Alternatives Rejected:**
  - *LangGraph / Heavy Multi-Agent Frameworks:* Rejected because their heavy abstractions obscured span-level debugging and introduced unnecessary dependencies for single-agent grounded retrieval.
  - *Cloud LLM APIs (GPT-4o / Claude Opus):* Rejected to honor the core TAE requirement of zero mandatory cloud spend and predictable local offline reproducibility.
  - *Unstructured Text Generation:* Rejected because downstream consumer systems suffer parse regressions when models hallucinate formatting.

---

### 3. Tools and Permissions

| Tool | Permission | Scope & Constraints |
|---|---|---|
| `search_corpus` | `read` | Full-text keyword search across `corpus/sample_docs/`. Read-only; cannot modify files. |
| `fetch_url` | `network` | Fetches HTTP/HTTPS web endpoints with a strict 8-second socket timeout and HTML stripping. |
| `run_code` | `compute` | Executes pure Python snippets in an in-memory namespace. Sandboxed: rejects imports (`ast.Import`) and dangerous builtins (`eval`, `exec`, `open`). |
| `write_file` | `write` | Writes text files strictly inside `agent_output/`. Rejects directory traversal (`../`) and absolute paths. |

---

### 4. How We Know It Works (Evaluation, Gating & Non-Determinism)
- **Evaluation Dimensions:** Evaluated using `evaluation/eval_harness.py` against a 20-item golden dataset (`evaluation/golden_dataset.jsonl`) measuring Groundedness Rate ($\ge 80\%$), Keyword Recall ($\ge 75\%$), and Latency (P95 $\le 15.0\text{ s}$), plus a 15-item adversarial red-team suite (`evaluation/red_team_prompts.jsonl`) measuring Security Block Rate ($\ge 90\%$).
- **Gating Mechanism:** The CI pipeline (`evaluation/ci_gate.py` and `deployment/ci_pipeline.yml`) runs on every commit and PR, immediately blocking merges if any threshold regresses.
- **Handling Non-Deterministic Answers:** Instead of brittle string matching, verification relies on:
  1. Invariant Pydantic schema conformity.
  2. Grounded claim overlap asserting that every answer proposition maps to an attested corpus snippet.
  3. Distributional testing over repeated trials ($N=5$) with statistical confidence intervals.
  *(See detailed ADR in [`evidence/module_01_decision_record.md`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_01_decision_record.md)).*

---

### 5. Honest Declaration: Three Known Weaknesses
1. **Concurrency Bottleneck & Memory Lock Contention:** The sequential synchronous ReAct loop and flat-file memory store (`.conversation_store.json`) lack transactional record locking and connection pooling; under concurrent user requests, sessions experience read/write race conditions and latency spikes without an async worker queue (e.g., Celery/Redis).
2. **Vulnerability to Multi-Turn Indirect Prompt Injection:** Hostile content embedded in fetched third-party web pages (`fetch_url`) or tainted corpus docs can steer intermediate reasoning thoughts and tool actions before the post-generation guardrail examines the final payload.
3. **Lexical Mismatch in Pure Keyword Retrieval:** Retrieval via `search_corpus` depends on unigram term overlap. Queries using synonyms or multi-hop conceptual reasoning miss relevant passages that a dense vector index (e.g., embeddings) would retrieve.

---

### 6. Declaration of Missing Artefacts & Substitutions
- **No Missing Required Artefacts:** All 13 course module evidence items are fully implemented, verified, and located in the [`evidence/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence) directory.
- **Sanctioned Cloud-Spend Substitution (Ground Rule 3):** To adhere strictly to the "no cloud spend required" mandate, the optional live Cloud Run container (Section 7) was not deployed to a paid billing account; instead, complete deployable container configurations (`deployment/Dockerfile`, `deployment/ci_pipeline.yml`, and `deployment/deploy_cloud.sh`) and local OpenTelemetry trace logs are provided as verifiable evidence.

---

### Evidence Directory Cross-Reference

| Evidence Artifact | Source Module | Path |
|---|---|---|
| Decision Record on Non-Determinism | Sprint 0, Module 1 | [`evidence/module_01_decision_record.md`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_01_decision_record.md) |
| Extended Test Suite & Spec | Sprint 1, Module 2 | [`evidence/module_02_test_suite/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_02_test_suite) |
| Structured Output & OOD Tests | Sprint 2, Module 3 | [`evidence/module_03_structured_output/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_03_structured_output) |
| Tool Failure Recovery Run | Sprint 3, Module 4 | [`evidence/module_04_agent_core/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_04_agent_core) |
| Cited Answers vs Sources | Sprint 4, Module 5 | [`evidence/module_05_grounded_answers/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_05_grounded_answers) |
| Eval Suite & Error Analysis | Sprint 5, Module 6 | [`evidence/module_06_eval_suite/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_06_eval_suite) |
| Failing Span Trace Walkthrough | Sprint 6, Module 7 | [`evidence/module_07_trace_debug/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_07_trace_debug) |
| Red Team Report & Guardrails | Sprint 7, Module 8 | [`evidence/module_08_red_team/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_08_red_team) |
| MCP Paused Run & Failed A2A Handoff | Sprint 8, Module 9 | [`evidence/module_09_orchestration/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_09_orchestration) |
| Browser Agent Web Run & Recovery | Sprint 9, Module 10 | [`evidence/module_10_browser_agent/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_10_browser_agent) |
| Pipeline Eval Gate & Deployment Config | Sprint 10, Module 11 | [`evidence/module_11_ci_gate/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_11_ci_gate) |
| Continuous Eval & Quality Alert | Sprint 10 (Cont.), Module 12 | [`evidence/module_12_continuous_eval/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_12_continuous_eval) |
| Model Card & Walkthrough Notes | Sprint 11, Module 13 | [`evidence/module_13_capstone/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evidence/module_13_capstone) |
