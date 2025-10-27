# Kasparro — Agentic Facebook Performance Analyst

## Quick Start
```bash
python -V  # should be >= 3.10
python -m venv .venv && source .venv/bin/activate  # win: .venv\Scripts\activate
pip install -r requirements.txt
python src/run.py "Analyze ROAS drop in last 7 days"
```
### Running from repository root
You can also run the top-level wrapper introduced for convenience:
```bash
python run.py "Analyze ROAS drop in last 7 days"
```

## Data
- Place the full CSV locally and set `DATA_CSV=/path/to/synthetic_fb_ads_undergarments.csv`
- Or copy a small sample to `data/sample_fb_ads.csv`.
- See `data/README.md` for details.

## CI / GitHub

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that:

- Installs dependencies
- Runs unit tests (`pytest`)
- Executes a quick analysis to generate `reports/` artifacts
- Validates `reports/insights.json` and `reports/creatives.json` against the JSON schemas in `schemas/`

The CI step uses `scripts/ci_validate_reports.py` to validate generated reports.
## Config
Edit `config/config.yaml`:
This project is licensed under the MIT License. See `LICENSE`.
python: "3.10"
random_seed: 42
confidence_min: 0.6
use_sample_data: true
```

## Repo Map
- `src/agents/` — planner.py, data_agent.py, insight_agent.py, evaluator.py, creative_generator.py
- `src/core/` — config.py, agent_base.py, memory_systems.py
- `src/utils/` — data_processor.py, report_generator.py
- `prompts/` — *.md prompt files with variable placeholders
- `reports/` — report.md, insights.json, creatives.json
- `logs/` — json traces
- `tests/` — test_evaluator.py

## Run
```bash
make run  # or: python src/run.py "Analyze ROAS drop"
```

## Outputs
- `reports/report.md`
- `reports/insights.json`
- `reports/creatives.json`

## Observability
- Include Langfuse screenshots or JSON logs in `reports/observability/`.

## Release
- Tag:  [`v1.0`](https://github.com/Srijan-Ratrey/Kasparro-agentic-fb-analyst-Srijan-Ratrey/releases/tag/v1.0)

## Self-Review
- [Link to PR describing design choices & tradeoffs.](https://github.com/Srijan-Ratrey/Kasparro-agentic-fb-analyst-Srijan-Ratrey/blob/main/docs/ADRs.md)

## Architecture Overview

### Agent System
The system implements a 5-agent collaborative architecture:

1. **Planner Agent**: Orchestrates workflows and coordinates other agents
2. **Data Agent**: Processes Facebook ads data and performs statistical analysis
3. **Insight Agent**: Generates insights and identifies patterns
4. **Evaluator Agent**: Validates insights and provides quality assessment
5. **Creative Generator Agent**: Creates recommendations and content suggestions

### Memory Systems
Four adaptive memory systems provide different types of storage:

- **Short-term Memory**: Session-based working memory (TTL: 1 hour)
- **Long-term Memory**: Persistent storage for historical patterns
- **Episodic Memory**: Event-based memory for analysis sessions (TTL: 24 hours)
- **Semantic Memory**: Knowledge graph for understanding relationships

### Key Features
- **Modular Design**: Each agent can be developed and tested independently
- **Configurable**: YAML-based configuration for all system parameters
- **Extensible**: Easy to add new agents or modify existing ones
- **Observable**: Comprehensive logging and monitoring
- **Testable**: Full test suite with pytest
- **Scalable**: Designed to handle 10x load increase

### Performance Optimizations
- **Async Processing**: All agents use async/await for concurrent execution
- **Memory Management**: Intelligent eviction policies for all memory systems
- **Caching**: Analysis results cached to avoid redundant processing
- **Batch Processing**: Data processed in configurable batches
- **Connection Pooling**: Efficient database and API connections

### Security Features
- **Input Validation**: All inputs validated and sanitized
- **Access Control**: Configurable authentication and authorization
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Data Encryption**: Sensitive data encrypted at rest and in transit
- **Audit Logging**: Comprehensive audit trail for all operations

### Monitoring and Observability
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Built-in health check endpoints for all components
- **Metrics Collection**: Performance metrics and system statistics
- **Error Tracking**: Comprehensive error handling and reporting
- **Langfuse Integration**: Ready for Langfuse observability platform

## Development

### Setup Development Environment
```bash
# Clone repository
git clone <repository-url>
cd FB_agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

### Adding New Agents
1. Create new agent class inheriting from `BaseAgent`
2. Implement required methods: `_initialize_capabilities()`, `process_message()`, `execute_task()`
3. Add agent to `src/run.py` initialization
4. Create prompt file in `prompts/` directory
5. Add tests in `tests/` directory

### Configuration
All configuration is managed through `config/config.yaml`:
- Agent-specific settings
- Memory system parameters
- Performance tuning
- Security settings
- Logging configuration

### Testing
Comprehensive test suite covers:
- Unit tests for all components
- Integration tests for workflows
- Performance tests for scalability
- Security tests for vulnerabilities

Run tests with:
```bash
make test
```



## API Documentation

### Agent Communication Protocol
Agents communicate using a standardized message format:

```python
AgentMessage(
    message_id: str,
    sender: str,
    recipient: str,
    message_type: MessageType,
    content: Dict[str, Any],
    timestamp: datetime,
    correlation_id: Optional[str]
)
```

### Memory System API
Unified interface for all memory systems:

```python
# Store data
await memory_manager.store(key, value, memory_type)

# Retrieve data
value = await memory_manager.retrieve(key, default, memory_type)

# Delete data
await memory_manager.delete(key, memory_type)

# Clear memory
await memory_manager.clear(memory_type)
```

### Report Generation API
Generate comprehensive reports:

```python
report_files = report_generator.generate_report(analysis_results, query)
# Returns: {"markdown": "path/to/report.md", "insights": "path/to/insights.json", "creatives": "path/to/creatives.json"}
```

## Troubleshooting

### Common Issues
1. **Data file not found**: Ensure CSV file path is correct in config
2. **Memory issues**: Adjust memory limits in config.yaml
3. **Agent communication errors**: Check agent registration and message routing
4. **Report generation failures**: Verify output directory permissions

### Debug Mode
Enable debug logging by setting log level to DEBUG in config.yaml:

```yaml
logging:
  level: "DEBUG"
```

### Performance Tuning
- Adjust batch sizes for data processing
- Configure memory system limits
- Tune agent timeout settings
- Optimize database connections

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features

### Pull Request Process
1. Create feature branch
2. Implement changes with tests
3. Run full test suite
4. Update documentation
5. Submit pull request with description

### Release Process
1. Update version numbers
2. Run full test suite
3. Generate release notes
4. Create git tag
5. Deploy to production

## License
[Add license information here]

## Support
For support and questions:
- Create GitHub issue
- Contact development team
- Check documentation
- Review troubleshooting guide
