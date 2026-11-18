# Evaluation as Engineering

Evaluating non-deterministic agentic systems requires moving beyond ad-hoc spot checks to quantitative, regression-tested evaluation pipelines.

## Evaluation Dimensions
1. Groundedness (Faithfulness): Does the generated response contain only claims supported by retrieved context?
2. Answer Relevance: Does the output directly answer the user prompt without irrelevant verbosity?
3. Tool Selection Precision: Did the agent invoke the correct tool with valid schema parameters on the first attempt?
4. Statistical Gating: Running evaluation suites across multiple repetitions calculates 95% confidence intervals to separate genuine regressions from model stochasticity.
