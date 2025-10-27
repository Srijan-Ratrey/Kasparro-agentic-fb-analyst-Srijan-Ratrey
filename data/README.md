# Data Directory

This directory contains data files and memory storage for the Agentic Facebook Performance Analyst system.

## Structure

```
data/
├── README.md                 # This file
├── memory/                   # Memory system storage
│   ├── long_term.json       # Long-term memory persistence
│   └── semantic_graph.json  # Semantic memory knowledge graph
└── sample_fb_ads.csv        # Sample data for testing (optional)
```

## Data Files

### Main Dataset
- **File**: `synthetic_fb_ads_undergarments.csv` (in project root)
- **Size**: ~792KB, 4,502 rows
- **Description**: Synthetic Facebook ads data for undergarments campaigns
- **Columns**: campaign_name, adset_name, date, spend, impressions, clicks, ctr, purchases, revenue, roas, creative_type, creative_message, audience_type, platform, country

### Sample Data
- **File**: `sample_fb_ads.csv` (optional)
- **Description**: Smaller subset of data for testing and development
- **Usage**: Set `use_sample_data: true` in config.yaml

## Memory Storage

### Long-term Memory
- **File**: `memory/long_term.json`
- **Purpose**: Persistent storage for historical patterns and learnings
- **Format**: JSON with memory data and metadata
- **Backup**: Automatically backed up on system shutdown

### Semantic Memory
- **File**: `memory/semantic_graph.json`
- **Purpose**: Knowledge graph for understanding relationships between metrics
- **Format**: JSON with nodes and edges representing knowledge relationships
- **Backup**: Automatically backed up on system shutdown

## Data Processing

The system automatically:
1. **Validates** data format and completeness
2. **Cleans** missing values and inconsistencies
3. **Transforms** data types and formats
4. **Enriches** data with calculated metrics
5. **Stores** processed data in memory systems

## Configuration

Data paths are configured in `config/config.yaml`:

```yaml
data_csv_path: "synthetic_fb_ads_undergarments.csv"
use_sample_data: false
sample_size: 1000
```

## Memory Configuration

Memory system settings:

```yaml
memory:
  long_term:
    max_items: 10000
    persistence_file: "data/memory/long_term.json"
  semantic:
    knowledge_graph_file: "data/memory/semantic_graph.json"
    max_nodes: 5000
```

## Data Privacy

- All data is processed locally
- No external data transmission
- Memory files contain only processed insights
- Original data remains in source CSV file

## Troubleshooting

### Data Loading Issues
- Verify CSV file exists and is readable
- Check file permissions
- Ensure proper CSV format
- Validate column names match expected schema

### Memory Issues
- Check available disk space
- Verify directory permissions
- Monitor memory usage
- Clear old memory files if needed

### Performance Issues
- Use sample data for development
- Adjust batch sizes in configuration
- Monitor memory system limits
- Optimize data processing parameters

## Backup and Recovery

### Automatic Backups
- Memory systems automatically save to disk
- Data is persisted on system shutdown
- Recovery happens automatically on startup

### Manual Backup
```bash
# Backup memory files
cp data/memory/long_term.json data/memory/long_term.json.backup
cp data/memory/semantic_graph.json data/memory/semantic_graph.json.backup

# Backup original data
cp synthetic_fb_ads_undergarments.csv data/synthetic_fb_ads_undergarments.csv.backup
```

### Recovery
```bash
# Restore from backup
cp data/memory/long_term.json.backup data/memory/long_term.json
cp data/memory/semantic_graph.json.backup data/memory/semantic_graph.json
```

## Data Analysis

The system provides comprehensive data analysis capabilities:

### Performance Metrics
- ROAS (Return on Ad Spend)
- CTR (Click-Through Rate)
- Conversion rates
- Cost per acquisition
- Revenue analysis

### Trend Analysis
- Time series analysis
- Seasonal pattern detection
- Growth trend identification
- Performance decline detection

### Anomaly Detection
- Statistical outlier identification
- Performance spike detection
- Data quality issue identification
- Unusual pattern recognition

### Comparative Analysis
- Campaign performance comparison
- Audience analysis
- Platform performance analysis
- Creative performance analysis

## Integration

The data system integrates with:
- **Agent System**: Provides data to all agents
- **Memory Systems**: Stores processed insights
- **Report Generator**: Creates analysis reports
- **Configuration System**: Manages data settings
- **Logging System**: Tracks data processing

## Monitoring

Data processing is monitored through:
- **Processing Logs**: Detailed logs of data operations
- **Performance Metrics**: Processing time and throughput
- **Error Tracking**: Data validation and processing errors
- **Memory Usage**: Memory system utilization
- **Quality Metrics**: Data completeness and accuracy

## Future Enhancements

Planned improvements:
- **Real-time Data Processing**: Stream processing capabilities
- **External Data Integration**: API connections for live data
- **Advanced Analytics**: Machine learning models
- **Data Visualization**: Interactive charts and graphs
- **Export Capabilities**: Multiple output formats
