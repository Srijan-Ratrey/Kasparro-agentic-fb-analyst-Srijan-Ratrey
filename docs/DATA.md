# DATA configuration and sample data

This project uses a synthetic dataset for local runs. The production dataset path is controlled by the `data_csv_path` key in `config/config.yaml` (or environment variable `DATA_CSV` if you prefer).

- Local sample: `data/sample_ads_120.csv` (small, ~120 rows) — included for quick testing.
- Full dataset (not included): `synthetic_fb_ads_undergarments.csv` — expected path relative to repository root.

How to run locally with sample data:

1. Edit `config/config.yaml` and set `use_sample_data: true` or point `data_csv_path` at `data/sample_ads_120.csv`.
2. Run:

```bash
python run.py "Analyze ROAS drop in last 7 days"
```

If you prefer to use an environment variable:

```bash
export DATA_CSV=/absolute/path/to/full_dataset.csv
# or run with the sample
export DATA_CSV=$(pwd)/data/sample_ads_120.csv
python run.py "Analyze ROAS drop in last 7 days"
```

Notes:
- The `data/` folder intentionally contains only a small sample for release hygiene. Do not commit full production datasets to the repository.
- For reproducible releases, publish an artifact (`reports/release_v1.0_result.json`) capturing a benchmark run as done for v1.0 in `reports/`.
