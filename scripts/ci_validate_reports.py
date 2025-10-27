"""CI helper: validate generated reports against JSON schemas.

This script expects `reports/insights.json` and `reports/creatives.json` to exist and `schemas/*.json` to be present.
"""
import json
import sys
from pathlib import Path

from jsonschema import validate, ValidationError

ROOT = Path(__file__).parent.parent
SCHEMAS = ROOT / "schemas"
REPORTS = ROOT / "reports"

schemas = {
    "insights": json.load(open(SCHEMAS / "insights.schema.json")),
    "creatives": json.load(open(SCHEMAS / "creatives.schema.json")),
}

errors = []

# Validate insights
insights_path = REPORTS / "insights.json"
if insights_path.exists():
    try:
        data = json.load(open(insights_path))
        validate(instance=data, schema=schemas["insights"])
        print("insights.json: OK")
    except ValidationError as e:
        errors.append(f"insights.json: {e}")
else:
    errors.append("insights.json: not found")

# Validate creatives
creatives_path = REPORTS / "creatives.json"
if creatives_path.exists():
    try:
        data = json.load(open(creatives_path))
        validate(instance=data, schema=schemas["creatives"])
        print("creatives.json: OK")
    except ValidationError as e:
        errors.append(f"creatives.json: {e}")
else:
    errors.append("creatives.json: not found")

if errors:
    print("Validation failed:")
    for e in errors:
        print(" - ", e)
    sys.exit(2)

print("All validations passed.")
