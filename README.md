# Grounded Research & QA Agent — TAE Track Capstone

**Author:** Siddharth Nanavati  
**Email:** sidnanavati@gmail.com  
**Track:** Test Automation Engineering (TAE) Track — Capstone Submission  
**Frozen Review Tag:** `v1.0.0-peer-review`  
**Target Environment:** 100% Local (Zero Cloud Spend)

---

## 🚀 Quick Overview

This repository contains a production-ready, fully local **Grounded Research & QA Agent** built as the capstone for the 13-module TAE track. The agent answers technical questions strictly grounded in a local document corpus, validates its own outputs using strict Pydantic schemas, logs execution traces with OpenTelemetry, defends against adversarial prompt injections, and blocks regressions via an automated CI quality gate.

---

## 📁 Repository Structure At a Glance

| Directory / File | Description |
|---|---|
| **[`SYSTEM.md`](SYSTEM.md)** | **1-page System Summary:** Core architecture, tools, evaluation metrics, 3 known weaknesses, and missing artifact declarations. |
| **[`RUN.md`](RUN.md)** | **15-Minute Local Setup Guide:** Step-by-step instructions for peer reviewers to run tests and evaluations offline. |
| **[`PEER_REVIEW_REPORT.md`](PEER_REVIEW_REPORT.md)** | **Peer Review Report:** Scored evaluation (94/100) assessing an agentic system against the official TAE rubric. |
| **[`agent/`](agent/)** | **Core Agent Engine:** ReAct loop (`core.py`), tool registry (`tools.py`), JSON conversation store (`memory.py`), structured outputs (`structured_output.py`), and multi-layer safety filters (`guardrails.py`). |
| **[`corpus/`](corpus/)** | **Knowledge Corpus:** 5 sample technical markdown documents covering testing, structured outputs, eval, red teaming, and observability. |
| **[`evaluation/`](evaluation/)** | **Evaluation & CI Gate:** 20-case golden dataset (`golden_dataset.jsonl`), 15-case red-team suite (`red_team_prompts.jsonl`), automated scorer (`eval_harness.py`), and release gate (`ci_gate.py`). |
| **[`evidence/`](evidence/)** | **13 Module Evidence Artifacts:** Verifiable proof for all modules (ADRs, test suites, tool recovery traces, OTel traces, red-team reports, MCP runs, browser runs, etc.). |
| **[`observability/`](observability/)** | **Telemetry:** OpenTelemetry tracer integration (`tracing.py`) and span debugging walkthrough (`trace_walkthrough.md`). |
| **[`orchestration/`](orchestration/)** | **Workflows:** MCP asynchronous pause/resume demo (`mcp_action.py`) and Agent-to-Agent (A2A) contract (`a2a_contract.json`). |
| **[`browser_agent/`](browser_agent/)** | **Browser Automation:** Playwright web workflow with autonomous DOM error recovery (`browser_workflow.py`). |
| **[`deployment/`](deployment/)** | **Deployment & CI:** Dockerfile, GitHub Actions CI workflow (`ci_pipeline.yml`), and cloud deployment script (`deploy_cloud.sh`). |
| **[`model_card/`](model_card/)** | **Model Card:** Comprehensive system & model documentation (`MODEL_CARD.md`). |
| **[`tests/`](tests/)** | **Unit Test Suite:** Pytest tests covering guardrails, tools, memory, and schema validation. |

---

## ⚡ How to Run in 2 Minutes

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit tests (12 passed in ~4s)
python -m pytest tests/ -v

# 3. Ask a question to the agent
python -c "from agent.core import Agent; a = Agent(); print(a.run('What are the core principles of agentic testing?'))"

# 4. Run the CI Quality Gate
python evaluation/ci_gate.py
```

> **Note on Offline Resilience:** If an LLM daemon (Ollama) is not running locally, the agent automatically engages its deterministic local engine. Everything runs **100% green without requiring background services or paid APIs**.

---

## 🛡️ Core Capabilities & Safeguards

1. **Deterministic Grounding:** Every claim is verified against retrieved text from the corpus; fabricated or ungrounded responses are rejected.
2. **Layered Guardrails:** Blocks direct/indirect prompt injection, SSN/Credit Card PII patterns, and malicious AST Python imports (`eval`, `exec`, `open`).
3. **Resilient Recovery:** Tool failures and network timeouts trigger autonomous fallback strategies rather than crashing the loop.
4. **Automated CI Quality Gate:** Enforces $\ge 80\%$ groundedness, $\ge 75\%$ keyword recall, and $\ge 90\%$ security block rate on every build.
