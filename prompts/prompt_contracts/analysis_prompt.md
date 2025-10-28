# Analysis Prompt Contract

This document defines a prompt contract and a human-facing scaffold for agentic analysis tasks.

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AnalysisPromptContract",
  "description": "Prompt contract for analysis agents. The contract enforces a Think → Analyze → Conclude scaffold and expects structured JSON output conforming to the `AnalysisResult` schema.",
  "type": "object",
  "properties": {
    "input": {
      "type": "object",
      "properties": {
        "query": {"type": "string"},
        "data_summary": {"type": "object"}
      },
      "required": ["query"]
    },
    "analysis": {
      "type": "object",
      "properties": {
        "think": {"type": "string", "description": "Internal chain-of-thought style notes (brief)."},
        "analysis_steps": {
          "type": "array",
          "items": {"type": "string"}
        },
        "findings": {"type": "object"},
        "recommendations": {
          "type": "array",
          "items": {"type": "object","properties":{"type":{"type":"string"},"recommendation":{"type":"string"}}}
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
      },
      "required": ["analysis_steps", "findings", "recommendations", "confidence"]
    }
  },
  "required": ["input", "analysis"]
}
```

---

## Think → Analyze → Conclude scaffold (human-facing)

Think: (brief internal reasoning notes — 1–3 short sentences)

Analyze:
1) Which data slices will we examine?
2) What statistical checks will we run (t-test, z-score, trend)?
3) What alternative hypotheses should be considered?

Conclude:
- Provide a small structured JSON matching the schema above. Keep `analysis.think` short and put chain-of-thought notes there. The agent should not print unstructured chain-of-thought in production logs; the `think` field is a short summary suitable for traceability.

### Example scaffold
```json
{
  "input": {
    "query": "Analyze CTR drop for Campaign X",
    "data_summary": {"total_records": 120}
  },
  "analysis": {
    "think": "CTR dropped after creative change; suspect creative and audience mismatch",
    "analysis_steps": [
      "examine creative-level CTR over last 30 days",
      "compare audience segments (lookalike vs retargeting)",
      "run t-test on CTR before/after creative deployment"
    ],
    "findings": {"creative_underperforming": true, "audience_shift": "increase in broad audience spend"},
    "recommendations": [{"type":"creative","recommendation":"Test new UGC style with clearer CTA"}],
    "confidence": 0.7
  }
}
```

Use this scaffold when sending prompts to reasoning agents. The schema above should be validated by the caller before accepting results into memory or making decisions.
