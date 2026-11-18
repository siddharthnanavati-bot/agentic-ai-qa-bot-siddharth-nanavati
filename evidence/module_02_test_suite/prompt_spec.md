# Prompt & Specification for AI-Assisted Test Extension (Module 2)

## Task Description
The initial unit test suite only tested basic happy-path memory persistence. An AI coding agent was prompted to generate adversarial edge cases and boundary assertions based on the technical specification below.

## Agent System Prompt
```
You are an expert QA Automation Engineer specializing in testing agentic memory and tool sandboxes.
Given the target module `agent/memory.py` and `agent/tools.py`:
1. Generate test cases for TTL expiration and stale session pruning.
2. Generate tests for forbidden imports and malicious AST patterns in `run_code`.
3. Generate tests for path traversal prevention in `write_file`.
Ensure all tests run green under pytest with zero flaky assertions.
```

## Resulting Test Suite
The extended test suite is saved in `test_suite_extended.py` and executes green.
