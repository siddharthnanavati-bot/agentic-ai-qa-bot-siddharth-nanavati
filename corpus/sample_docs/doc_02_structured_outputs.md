# Foundation Models and Structured Outputs

In production agentic architectures, unstructured text output from foundation models introduces parse failures and schema regressions.

## Enforcement Strategies
- JSON Schema Enforcement: Constraining model generation using grammar-based sampling or function calling protocols ensures 100% syntactic conformity.
- Pydantic Validation: Runtime validation layers trap out-of-bounds metrics (e.g. confidence scores outside [0.0, 1.0]) and missing citation sources.
- Out-of-Distribution (OOD) Handling: Detecting queries outside known domain spaces ensures agents gracefully refuse rather than hallucinating plausible false schemas.
