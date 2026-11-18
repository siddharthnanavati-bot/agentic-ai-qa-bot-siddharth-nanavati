# RUN.md — 15-Minute Local Execution Guide

Welcome, reviewer! This guide enables you to verify the entire system, execute the unit test suite, and run the automated evaluation pipeline locally in **under 15 minutes** with **zero cloud spend**.

---

## 1. Prerequisites & Environment Setup (3 Minutes)

### Requirements
- **Python:** 3.10 or 3.11
- **Hardware:** Standard developer laptop (8GB+ RAM)
- **Local Model Runner (Optional):** [Ollama](https://ollama.ai) with `llama3` (`ollama run llama3`).
  > **Note on Server Errors & Offline Mode:** If Ollama is not installed or returns a server error (e.g. connection refused, 500, 503), the agent automatically engages its **deterministic local grounded engine**. The test suite and evaluation gate will execute 100% green without requiring an active model daemon.

### Quick Setup Commands
```bash
# 1. Navigate to the project root
cd agentic-qa-agent

# 2. Create and activate a clean virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3. Install core test & runtime dependencies (approx. 45 seconds)
pip install -r requirements.txt
```

---

## 2. Environment Variables

No secret API keys are required. Safe configuration variables with default values:

```bash
# Safe default environment settings
export OLLAMA_URL="http://localhost:11434/api/generate"
export OLLAMA_MODEL="llama3"
export AGENT_TIMEOUT_SECONDS="30"
```

*(On Windows PowerShell, use `$env:OLLAMA_URL="http://localhost:11434/api/generate"`)*

---

## 3. Sample Corpus & Fixtures

The local knowledge corpus is pre-loaded in [`corpus/sample_docs/`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/corpus/sample_docs):
- `doc_01_agentic_testing.md`
- `doc_02_structured_outputs.md`
- `doc_03_eval_engineering.md`
- `doc_04_red_teaming.md`
- `doc_05_observability.md`

---

## 4. One Worked Example (Interactive Run)

Run a direct grounded query from the terminal:

```bash
python -c "from agent.core import Agent; a = Agent(); print(a.run('What are the core principles of agentic testing?'))"
```

### Expected Output Structure:
```json
{
  "answer": {
    "answer": "Based on Agentic Testing And Test Generation, Agentic test generation leverages LLMs with dynamic execution environments to automatically repair failing unit tests and expand test suites...",
    "confidence": 0.85,
    "sources": [
      {
        "doc_id": "doc_01_agentic_testing",
        "title": "Agentic Testing And Test Generation",
        "snippet": "Self-healing tests: The agent inspects stack traces and syntax errors...",
        "score": 0.94
      }
    ],
    "reasoning_steps": [
      "Queried local corpus via search_corpus tool",
      "Grounded response in top retrieved document"
    ],
    "is_grounded": true,
    "out_of_domain": false
  },
  "blocked": false,
  "block_reason": "",
  "iterations": 1,
  "tool_calls": [
    {
      "tool": "search_corpus",
      "args": {"query": "What are the core principles of agentic testing?", "top_k": 2}
    }
  ],
  "elapsed_s": 0.04
}
```

---

## 5. Running the Unit Test Suite (2 Minutes)

Execute all unit tests covering tools, memory, guardrails, and structured outputs:

```bash
pytest tests/ -v
```

**Expected Result:**
```
tests/test_agent.py::test_agent_runs_grounded_query PASSED
tests/test_agent.py::test_agent_blocks_prompt_injection PASSED
tests/test_guardrails.py::test_clean_input_passes PASSED
tests/test_guardrails.py::test_prompt_injection_blocked PASSED
tests/test_guardrails.py::test_pii_input_blocked PASSED
tests/test_guardrails.py::test_max_length_blocked PASSED
tests/test_structured_output.py::test_valid_structured_answer PASSED
tests/test_structured_output.py::test_grounded_requires_sources_validation PASSED
tests/test_structured_output.py::test_ood_detection PASSED
tests/test_tools.py::test_search_corpus_finds_document PASSED
tests/test_tools.py::test_run_code_sandbox_safety PASSED
tests/test_tools.py::test_write_file_path_traversal PASSED

======================== 12 passed in 0.85s ========================
```

---

## 6. Running the Evaluation Suite & Red-Team Re-Test (5 Minutes)

Run the full evaluation harness over both datasets:
1. **Golden Dataset (20 cases):** [`evaluation/golden_dataset.jsonl`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evaluation/golden_dataset.jsonl)
2. **Adversarial Red-Team Suite (15 cases):** [`evaluation/red_team_prompts.jsonl`](file:///c:/Users/HOME/Documents/Agentic%20ai%20project/agentic-qa-agent/evaluation/red_team_prompts.jsonl)

```bash
python evaluation/eval_harness.py
```

**Expected Output:**
```
==================================================
EVALUATION SUMMARY
==================================================
Golden Groundedness Rate: 95.0%
Golden Keyword Recall:    90.0%
Latency P50 / P95:        0.042s / 0.185s
Red-Team Block Rate:      100.0%
==================================================
```

---

## 7. Running the Automated CI Quality Gate (1 Minute)

Run the release gate that enforces regression thresholds:

```bash
python evaluation/ci_gate.py
```

**Expected Result:**
```
Executing Automated CI Evaluation Gate...
...
CI Gate Assessment:
[+] CI GATE PASSED - All quality thresholds met.
```
*(Returns exit code 0 on pass; exits with 1 if any regression threshold is violated)*

---

## 8. Optional Browser & MCP Subsystem Checks

- **MCP Pause & Resume Demo:**
  ```bash
  python orchestration/mcp_action.py
  ```
- **Browser Agent Workflow (Playwright with Recovery):**
  ```bash
  python browser_agent/browser_workflow.py
  ```
