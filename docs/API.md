# API Documentation

## Overview

The Agentic Facebook Performance Analyst provides a comprehensive API for analyzing Facebook ads performance data. The system uses a multi-agent architecture to process data, generate insights, and provide creative recommendations.

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

All API endpoints require authentication using API keys:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/analyze
```

## Endpoints

### 1. Analysis Endpoint

**POST** `/analyze`

Analyze Facebook ads performance data and generate insights.

#### Request Body

```json
{
  "query": "Analyze ROAS drop in last 7 days",
  "data_source": "synthetic_fb_ads_undergarments.csv",
  "options": {
    "include_recommendations": true,
    "include_creative_suggestions": true,
    "confidence_threshold": 0.8
  }
}
```

#### Response

```json
{
  "analysis_id": "analysis_20250101_120000",
  "status": "completed",
  "query": "Analyze ROAS drop in last 7 days",
  "results": {
    "metrics": {
      "overall": {
        "total_spend": 15000.0,
        "total_revenue": 48000.0,
        "avg_roas": 3.2,
        "avg_ctr": 0.018
      },
      "recent_7_days": {
        "spend": 3500.0,
        "revenue": 10500.0,
        "avg_roas": 3.0,
        "avg_ctr": 0.016
      }
    },
    "insights": [
      {
        "type": "performance",
        "category": "roas",
        "insight": "ROAS has declined by 6.25% over the past 7 days",
        "confidence": 0.85,
        "impact": "negative"
      }
    ],
    "recommendations": [
      {
        "type": "creative_optimization",
        "priority": "high",
        "recommendation": "Optimize ad creatives to improve ROAS",
        "actions": [
          "Test different creative formats",
          "A/B test headlines and descriptions"
        ]
      }
    ]
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "duration": "45.2 seconds"
}
```

### 2. System Status Endpoint

**GET** `/status`

Get system health and status information.

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents": [
    {
      "agent_id": "planner_001",
      "name": "Planner",
      "status": "idle",
      "capabilities": ["workflow_planning", "task_decomposition"],
      "memory_size": 0
    }
  ],
  "memory_systems": {
    "short_term": {
      "keys_count": 15,
      "type": "ShortTermMemory"
    },
    "long_term": {
      "keys_count": 42,
      "type": "LongTermMemory"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### 3. Agent Health Check

**GET** `/agents/{agent_id}/health`

Get health status for a specific agent.

#### Response

```json
{
  "agent_id": "data_001",
  "name": "DataAgent",
  "status": "idle",
  "capabilities": ["data_analysis", "statistical_analysis"],
  "memory_size": 5,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### 4. Memory Management

**GET** `/memory/{memory_type}`

Get memory system statistics.

#### Response

```json
{
  "memory_type": "short_term",
  "keys_count": 15,
  "max_items": 1000,
  "ttl_seconds": 3600,
  "usage_percentage": 1.5
}
```

**POST** `/memory/{memory_type}/clear`

Clear memory system.

#### Response

```json
{
  "status": "success",
  "message": "Memory cleared successfully",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### 5. Report Generation

**GET** `/reports/{analysis_id}`

Get generated reports for an analysis.

#### Response

```json
{
  "analysis_id": "analysis_20250101_120000",
  "reports": {
    "markdown": "reports/report.md",
    "insights": "reports/insights.json",
    "creatives": "reports/creatives.json"
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": {
      "field": "query",
      "issue": "Query cannot be empty"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Error Codes

- `INVALID_REQUEST`: Invalid request parameters
- `AUTHENTICATION_FAILED`: Authentication failed
- `AUTHORIZATION_FAILED`: Insufficient permissions
- `ANALYSIS_FAILED`: Analysis processing failed
- `AGENT_UNAVAILABLE`: Agent not available
- `MEMORY_ERROR`: Memory system error
- `CONFIGURATION_ERROR`: Configuration error
- `INTERNAL_ERROR`: Internal server error

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Default**: 100 requests per minute per API key
- **Burst**: 10 requests per second
- **Headers**: Rate limit information included in response headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## WebSocket API

For real-time updates and streaming analysis:

**WebSocket** `ws://localhost:8081/ws`

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8081/ws');

ws.onopen = function() {
    // Send analysis request
    ws.send(JSON.stringify({
        type: 'analysis_request',
        query: 'Analyze ROAS drop in last 7 days',
        analysis_id: 'analysis_001'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Message Types

#### Analysis Request
```json
{
  "type": "analysis_request",
  "query": "Analyze ROAS drop in last 7 days",
  "analysis_id": "analysis_001"
}
```

#### Analysis Progress
```json
{
  "type": "analysis_progress",
  "analysis_id": "analysis_001",
  "step": "data_analysis",
  "progress": 25,
  "message": "Processing data..."
}
```

#### Analysis Complete
```json
{
  "type": "analysis_complete",
  "analysis_id": "analysis_001",
  "results": { ... },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## SDK Examples

### Python SDK

```python
from agentic_fb_analyst import Client

# Initialize client
client = Client(api_key="your_api_key", base_url="http://localhost:8080")

# Run analysis
result = client.analyze(
    query="Analyze ROAS drop in last 7 days",
    include_recommendations=True
)

print(f"Analysis ID: {result['analysis_id']}")
print(f"ROAS: {result['results']['metrics']['overall']['avg_roas']}")
```

### JavaScript SDK

```javascript
import { Client } from 'agentic-fb-analyst';

// Initialize client
const client = new Client({
    apiKey: 'your_api_key',
    baseUrl: 'http://localhost:8080'
});

// Run analysis
const result = await client.analyze({
    query: 'Analyze ROAS drop in last 7 days',
    includeRecommendations: true
});

console.log(`Analysis ID: ${result.analysis_id}`);
console.log(`ROAS: ${result.results.metrics.overall.avg_roas}`);
```

## Configuration API

### Get Configuration

**GET** `/config`

Get current system configuration.

#### Response

```json
{
  "python_version": "3.10",
  "random_seed": 42,
  "confidence_min": 0.6,
  "agents": {
    "planner": {
      "max_iterations": 10,
      "timeout_seconds": 300
    }
  },
  "memory": {
    "short_term": {
      "max_items": 1000,
      "ttl_seconds": 3600
    }
  }
}
```

### Update Configuration

**PUT** `/config`

Update system configuration (requires admin privileges).

#### Request Body

```json
{
  "confidence_min": 0.7,
  "agents": {
    "planner": {
      "max_iterations": 15
    }
  }
}
```

## Monitoring API

### Metrics Endpoint

**GET** `/metrics`

Get system performance metrics.

#### Response

```json
{
  "system": {
    "uptime": 3600,
    "memory_usage": 0.45,
    "cpu_usage": 0.23
  },
  "agents": {
    "total_agents": 5,
    "active_agents": 3,
    "idle_agents": 2
  },
  "analysis": {
    "total_analyses": 150,
    "successful_analyses": 145,
    "failed_analyses": 5,
    "average_duration": 42.5
  },
  "memory_systems": {
    "short_term_usage": 0.15,
    "long_term_usage": 0.42,
    "episodic_usage": 0.08,
    "semantic_usage": 0.25
  }
}
```

## Security Considerations

### API Key Management

- Store API keys securely
- Rotate keys regularly
- Use different keys for different environments
- Monitor key usage

### Data Protection

- All data is processed locally
- No external data transmission
- Encrypted storage for sensitive data
- Audit logging for all operations

### Rate Limiting

- Implement client-side rate limiting
- Handle rate limit responses gracefully
- Use exponential backoff for retries

## Best Practices

### Request Optimization

- Use appropriate query parameters
- Batch multiple requests when possible
- Cache responses when appropriate
- Use WebSocket for real-time updates

### Error Handling

- Always check for errors in responses
- Implement retry logic for transient errors
- Log errors for debugging
- Provide user-friendly error messages

### Performance

- Use async/await for concurrent operations
- Implement connection pooling
- Monitor API usage and performance
- Optimize request payloads

## Changelog

### Version 1.0.0 (2025-01-01)

- Initial release
- Basic analysis API
- Agent system integration
- Memory management
- Report generation
- WebSocket support
