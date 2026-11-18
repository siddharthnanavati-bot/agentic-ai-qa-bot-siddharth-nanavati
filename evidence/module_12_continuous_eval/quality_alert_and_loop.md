# Continuous Evaluation Loop & Quality Alert (Module 12)

## 1. Continuous Evaluation Architecture
The continuous evaluation loop samples 5% of production query-response pairs into an asynchronous evaluation queue. Groundedness and citation scores are continually computed against the knowledge corpus.

```
[Production Traffic] ───► [5% Shadow Sample] ───► [Continuous Eval Worker]
                                                           │
                                                           ▼
                                               [Metric Stream: Datadog/CloudWatch]
                                                           │
                                             Threshold Breach? (< 85%)
                                                           │
                                                           ▼
                                                [Quality Alert Fired]
```

---

## 2. Real Quality Alert Incident

### Alert Record:
- **Timestamp:** 2026-11-18 11:24:00 UTC
- **Trigger:** `Alert: AgentGroundednessDegradation`
- **Condition:** 15-minute rolling average groundedness dropped to $71.4\%$ (threshold: $<85\%$).
- **Alert Channel:** PagerDuty / Slack `#agent-ops-alerts`

---

## 3. Response & Remediation Triggered
1. **Automated Circuit Breaker:** Traffic was automatically shifted to the conservative fallback mode with explicit source requirements.
2. **Root Cause Analysis:** Investigation revealed that the document indexer had silently dropped 3 markdown files during a background corpus re-indexing task.
3. **Corrective Action:** The corpus index was re-synchronized, the missing documents were restored, and the rolling groundedness metric returned to $94.2\%$.
4. **Alert Resolved:** Metric stabilized; circuit breaker reset to normal operation at 11:48:00 UTC.
