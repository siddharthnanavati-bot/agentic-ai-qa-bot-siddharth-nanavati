# Red Teaming and Adversarial Testing

Adversarial testing systematically probes agentic systems for security vulnerabilities, prompt injection, and harmful output generation.

## Attack Vectors
1. Direct Prompt Injection: Attackers instruct the model to disregard previous constraints or reveal internal system prompts.
2. Indirect Prompt Injection: Malicious instructions embedded inside retrieved corpus documents or web pages hijack agent tool execution.
3. Guardrail Hardening: Layered defense comprising input sanitization, output pattern filtering, and runtime sandbox restrictions on dangerous tools.
