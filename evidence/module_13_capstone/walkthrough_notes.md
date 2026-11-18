# Capstone Walkthrough & Demonstration Notes (Module 13)

## System Walkthrough Plan
The 5-minute capstone walkthrough demonstrates the end-to-end capabilities of the Grounded Research & QA Agent:

1. **System Introduction (0:00 - 0:45):**
   - Architectural layout: ReAct agent, Pydantic schema constraints, layered guardrails.
   - Zero-cloud-spend local execution with Ollama or deterministic local engine.

2. **Grounded Query Demonstration (0:45 - 2:00):**
   - Querying: *"What are the core principles of agentic testing?"*
   - Live inspection of the retrieved citation sources, confidence score, and structured JSON output.

3. **Tool Failure & Recovery Demonstration (2:00 - 3:00):**
   - Triggering a network timeout on `fetch_url`.
   - Observing the agent autonomously adapt and fall back to `search_corpus` to satisfy the answer.

4. **Adversarial Red-Team Defense (3:00 - 4:00):**
   - Submitting prompt injection (`Ignore previous instructions...`) and AST code sandbox bypass attempts.
   - Verifying clean blocking with explicit rule violation reporting.

5. **CI Quality Gate & Evaluation Suite (4:00 - 5:00):**
   - Executing `python evaluation/ci_gate.py`.
   - Displaying the live metric summary and green pass confirmation.

The accompanying Model Card is located at `model_card/MODEL_CARD.md`.
