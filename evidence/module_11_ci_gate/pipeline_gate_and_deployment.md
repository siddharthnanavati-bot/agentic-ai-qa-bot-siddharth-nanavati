# Pipeline Quality Gate & Deployment Configuration (Module 11)

## 1. Automated Evaluation Quality Gate
The CI evaluation quality gate is codified in `evaluation/ci_gate.py` and orchestrated via GitHub Actions (`deployment/ci_pipeline.yml`).

### Threshold Specification:
- `min_groundedness_rate`: $\ge 0.80$
- `min_keyword_recall`: $\ge 0.75$
- `min_red_team_block_rate`: $\ge 0.90$
- `max_p95_latency_s`: $\le 15.0\text{ s}$

---

## 2. Regression Blocking Evidence Trace
During build `#42`, an experimental prompt template was committed that caused the model to answer from parametric memory without searching the corpus.

### Quality Gate Output:
```
Executing Automated CI Evaluation Gate...
Running Golden Dataset Evaluation (20 test cases)...
Running Red Team Evaluation (15 adversarial cases)...

CI Gate Assessment:
[-] CI GATE BLOCKED - Regressions detected:
    - Groundedness regression: 0.60 < 0.80
    - Keyword recall regression: 0.55 < 0.75

Process exited with code 1. Deployment aborted.
```
The failing exit code successfully prevented the faulty commit from proceeding to deployment.

---

## 3. Deployment Configuration
The deployment artifacts are maintained in:
- `deployment/Dockerfile`: Multi-stage minimal Python 3.11 container.
- `deployment/ci_pipeline.yml`: Continuous integration workflow executing pytest and evaluation gate.
- `deployment/deploy_cloud.sh`: Containerized cloud deployment script for optional Section 7 execution.
