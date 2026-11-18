# Model & System Card: Grounded Research & QA Agent

## 1. System Overview
- **Name:** Grounded Research & QA Agent
- **Version:** 1.0.0 (TAE Capstone Submission)
- **Primary Foundation Model:** Meta Llama 3 (8B Instruct, quantized via Ollama)
- **Architecture:** ReAct (Reason + Act) tool-augmented retrieval agent with Pydantic structured output validation and multi-layer safety guardrails.
- **Intended Use:** High-precision question answering and technical research synthesis strictly grounded in local corpora with explicit citation references.

## 2. Intended Domain & Out-of-Domain Boundaries
- **In-Scope:** Software engineering testing, agentic AI frameworks, structured data validation, evaluation engineering, observability, red teaming.
- **Out-of-Scope (Handled via OOD rejection):** Medical diagnosis, speculative financial advice, recipe generation, legal counseling, direct system-level arbitrary code execution.

## 3. Evaluation Metrics & Benchmark Performance
Evaluated across 20 grounded benchmark Q&A pairs and 15 adversarial red-team attack vectors:
- **Groundedness / Faithfulness:** 95.0%
- **Citation Recall:** 90.0%
- **Adversarial Block Rate:** 100.0%
- **Latency (P50 / P95):** 0.42s / 1.85s (local hardware)

## 4. Safety Guardrails & Operational Constraints
- **Input Filtering:** Regex-based prompt injection detection, token marker scrubbing, PII pattern masking, maximum input length ceiling (2,000 characters).
- **Tool Sandbox:** Prohibits `import` statements and dangerous builtins (`eval`, `exec`, `open`) in `run_code`; blocks path traversal (`../`) in `write_file`.
- **Output Validation:** Rejects parametric knowledge hallucinations and catches ungrounded disclaimer leakage.

## 5. Walkthrough Video & Demo Notes
- Walkthrough script and screen recording notes: `evidence/module_13_capstone/walkthrough_notes.md`
