# Trace Walkthrough: Debugging a Degraded Agent Response (Module 7)

## Incident Overview
During regression testing, Query `Q-849` ("Summarize the latest deployment gate configurations") returned a degraded, low-confidence answer ($0.25$) after experiencing an elevated total latency of $12.4\text{ s}$ (baseline: $<1.5\text{ s}$).

Below is the OpenTelemetry span breakdown captured during the run.

---

## Span Hierarchy & Timeline

```
[Trace ID: 7f3b1e90-d41a-45c1-92be-cf441e8c95a2]
└── root: agent.run (duration: 12.42s, status: OK)
    ├── span_01: guardrails.check_input (duration: 0.002s, status: OK)
    ├── span_02: agent.react_cycle.iter_1 (duration: 3.12s, status: OK)
    │   └── span_02a: llm.generate_prompt (duration: 3.10s, status: OK)
    │       └── event: action_selected = "fetch_url"
    ├── span_03: tool.fetch_url (duration: 8.01s, status: ERROR)  <-- FAILING SPAN
    │   ├── attr: url = "https://internal-docs.local/staging/ci-gate"
    │   ├── attr: timeout_limit = 8.0s
    │   ├── event: exception = "urllib.error.URLError: <urlopen error timed out>"
    │   └── attr: retry_attempt = 1 (failed)
    ├── span_04: agent.react_cycle.iter_2 (duration: 1.28s, status: OK)
    │   ├── event: observation = "Tool 'fetch_url' failed: connection timed out"
    │   └── span_04a: tool.search_corpus (duration: 0.008s, status: OK)
    │       └── attr: query = "deployment gate configurations"
    └── span_05: guardrails.check_output (duration: 0.001s, status: OK)
```

---

## Root Cause Analysis
1. **Failing Span:** `span_03` (`tool.fetch_url`).
2. **Failure Mechanism:** The agent decided to invoke `fetch_url` against an unreachable local domain. The network request stalled until hitting the default socket timeout of $8.0\text{ s}$.
3. **Recovery Execution:**
   - The agent caught the exception and generated an error observation.
   - On iteration 2 (`span_04`), the ReAct planner identified the tool error observation and gracefully fell back to `search_corpus`.
   - The corpus retriever succeeded in $8\text{ ms}$, extracting the grounded evidence from `doc_03_eval_engineering.md`.
4. **Permanent Fix Applied:**
   - Reduced `fetch_url` timeout to $3.0\text{ s}$.
   - Added domain pre-check to prevent attempted network calls to unreachable internal domains.
