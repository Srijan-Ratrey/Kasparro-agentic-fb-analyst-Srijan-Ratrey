# Self-Review

This branch contains a short self-review to accompany the v1.0 release.

Design choices

- Agented architecture: separated concerns into Planner, DataAgent, InsightAgent, Evaluator, and CreativeGenerator to allow independent development, testability, and clear data flow.
- Reproducibility: pinned random seed in `config/config.yaml` and added `use_sample_data` flag for quick runs.
- Explainability: creative recommendations now include `rationale`, `supporting_insights`, `confidence`, `expected_uplift`, and `ab_tests` to make suggestions actionable.
- Validation: added JSON Schemas in `schemas/` and a CI validation script `scripts/ci_validate_reports.py`.

How to reproduce outputs

1. Create a Python 3.10+ virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the analysis (sample):

```bash
python run.py "Analyze ROAS drop in last 7 days"
```

3. Generated outputs will be in `reports/`.

Notes & limitations

- The current repository contains a simulation in `src/agents/planner.py` for local testing; in production the planner would route messages to independent agent services.
- Expected uplift numbers are heuristic defaults; recommended to calibrate with historical A/B results.

