# JSON Schemas for Reports

This folder contains JSON Schema files describing the structure of the generated report artifacts.

Files:
- `insights.schema.json` — Schema for `reports/insights.json`.
- `creatives.schema.json` — Schema for `reports/creatives.json`.

Quick field guide

- analysis_id: string. Unique identifier or the query used for the analysis.
- timestamp: ISO datetime when the analysis was run.
- insights: Array of insight objects. Each insight typically contains: `type`, `category`, `insight` (text), `confidence` (0-1), `impact`.
- recommendations (in both schemas): Array of recommendation objects. Key fields include:
  - recommendation: human-readable action
  - rationale: short text explaining why
  - supporting_insights: list of insight keys or categories that justify the recommendation
  - confidence: numeric 0..1
  - expected_uplift: numeric fraction (e.g., 0.12 = 12%)
  - supporting_metrics: object with numeric context (e.g., avg_roas, avg_ctr)
  - ab_tests: optional object describing a recommended A/B test

Usage

- Use a JSON Schema validator (e.g., `ajv`, Python `jsonschema`) to validate generated artifacts in `reports/`.
- Example (Python):

```python
from jsonschema import validate
import json

schema = json.load(open('schemas/creatives.schema.json'))
data = json.load(open('reports/creatives.json'))
validate(instance=data, schema=schema)
```

These schemas are intentionally permissive for some fields so the agents can add extra metadata over time. If you want stricter validation, we can tighten required fields and types.
