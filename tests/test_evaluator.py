"""
Test suite for the Agentic Facebook Performance Analyst system.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime

# Import the modules to test
import sys
sys.path.append('src')

from src.core.config import Config
from src.core.agent_base import BaseAgent, AgentMessage, MessageType, AgentStatus
from src.utils.data_processor import FacebookAdsDataProcessor
from src.utils.report_generator import ReportGenerator
from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_generator import CreativeGeneratorAgent


class TestConfig:
    """Test configuration management."""
    
    def test_config_loading(self):
        """Test configuration loading from YAML."""
        config = Config("config/config.yaml")
        
        assert config.python_version == "3.10"
        assert config.random_seed == 42
        assert config.confidence_min == 0.6
        assert config.data_csv_path == "synthetic_fb_ads_undergarments.csv"
    
    def test_config_get_method(self):
        """Test configuration get method with dot notation."""
        config = Config("config/config.yaml")
        
        assert config.get("python") == "3.10"
        assert config.get("agents.planner.max_iterations") == 10
        assert config.get("mcp_server.host") == "localhost"
        assert config.get("nonexistent.key", "default") == "default"
    
    def test_agent_config(self):
        """Test agent-specific configuration."""
        config = Config("config/config.yaml")
        
        planner_config = config.get_agent_config("planner")
        assert planner_config["max_iterations"] == 10
        assert planner_config["timeout_seconds"] == 300
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config("config/config.yaml")
        
        # Should not raise an exception for valid config
        assert config.validate() == True


class TestDataProcessor:
    """Test data processing functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'campaign_name': ['Campaign A', 'Campaign B', 'Campaign A'],
            'date': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03']),
            'spend': [100.0, 200.0, 150.0],
            'impressions': [1000, 2000, 1500],
            'clicks': [50, 100, 75],
            'ctr': [0.05, 0.05, 0.05],
            'purchases': [5, 10, 7],
            'revenue': [500.0, 1000.0, 750.0],
            'roas': [5.0, 5.0, 5.0],
            'creative_type': ['Image', 'Video', 'UGC'],
            'audience_type': ['Broad', 'Lookalike', 'Retargeting'],
            'platform': ['Facebook', 'Instagram', 'Facebook'],
            'country': ['US', 'US', 'UK']
        })
    
    def test_data_processor_initialization(self, sample_data):
        """Test data processor initialization."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            processor = FacebookAdsDataProcessor(f.name)
            assert processor.df is not None
            assert len(processor.df) == 3
            
            # Clean up
            Path(f.name).unlink()
    
    def test_data_summary(self, sample_data):
        """Test data summary generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            processor = FacebookAdsDataProcessor(f.name)
            summary = processor.get_data_summary()
            
            assert summary['total_records'] == 3
            assert summary['total_spend'] == 450.0
            assert summary['total_revenue'] == 2250.0
            assert summary['avg_roas'] == 5.0
            
            # Clean up
            Path(f.name).unlink()
    
    def test_campaign_performance(self, sample_data):
        """Test campaign performance analysis."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            processor = FacebookAdsDataProcessor(f.name)
            campaign_perf = processor.get_campaign_performance()
            
            assert len(campaign_perf) == 2  # Two unique campaigns
            assert 'Campaign A' in campaign_perf['campaign_name'].values
            assert 'Campaign B' in campaign_perf['campaign_name'].values
            
            # Clean up
            Path(f.name).unlink()
    
    def test_anomaly_detection(self, sample_data):
        """Test anomaly detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            processor = FacebookAdsDataProcessor(f.name)
            anomalies = processor.detect_anomalies('roas', 2.0)
            
            # With consistent ROAS values, no anomalies should be detected
            assert len(anomalies) == 0
            
            # Clean up
            Path(f.name).unlink()
    
    def test_trend_calculation(self, sample_data):
        """Test trend calculation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            processor = FacebookAdsDataProcessor(f.name)
            trends = processor.calculate_trends('roas', 3)
            
            assert 'trend' in trends
            assert 'change_percent' in trends
            assert 'current_value' in trends
            
            # Clean up
            Path(f.name).unlink()


class TestAgentBase:
    """Test base agent functionality."""
    
    def test_agent_message_creation(self):
        """Test agent message creation and serialization."""
        message = AgentMessage(
            message_id="test_001",
            sender="test_sender",
            recipient="test_recipient",
            message_type=MessageType.REQUEST,
            content={"test": "data"},
            timestamp=datetime.now()
        )
        
        # Test serialization
        message_dict = message.to_dict()
        assert message_dict["message_id"] == "test_001"
        assert message_dict["sender"] == "test_sender"
        assert message_dict["message_type"] == "request"
        
        # Test deserialization
        restored_message = AgentMessage.from_dict(message_dict)
        assert restored_message.message_id == "test_001"
        assert restored_message.sender == "test_sender"
        assert restored_message.message_type == MessageType.REQUEST


class TestPlannerAgent:
    """Test planner agent functionality."""
    
    @pytest.fixture
    def planner_agent(self):
        """Create planner agent for testing."""
        config = {"max_iterations": 10, "timeout_seconds": 300}
        return PlannerAgent("planner_001", "Planner", config)
    
    def test_planner_initialization(self, planner_agent):
        """Test planner agent initialization."""
        assert planner_agent.agent_id == "planner_001"
        assert planner_agent.name == "Planner"
        assert planner_agent.status == AgentStatus.IDLE
        assert len(planner_agent.capabilities) > 0
    
    def test_planner_capabilities(self, planner_agent):
        """Test planner agent capabilities."""
        capabilities = planner_agent.get_capabilities()
        
        capability_names = [cap.name for cap in capabilities]
        assert "workflow_planning" in capability_names
        assert "task_decomposition" in capability_names
        assert "agent_coordination" in capability_names
    
    def test_planner_workflow_planning(self, planner_agent):
        """Test workflow planning functionality."""
        task = {
            "task_type": "workflow_planning",
            "query": "Analyze ROAS drop in last 7 days",
            "data_summary": {"total_records": 1000}
        }
        
        result = asyncio.run(planner_agent.execute_task(task))
        
        assert "workflow" in result
        assert "estimated_duration" in result
        assert "required_agents" in result
        assert len(result["workflow"]) > 0


class TestDataAgent:
    """Test data agent functionality."""
    
    @pytest.fixture
    def data_agent(self):
        """Create data agent for testing."""
        config = {"batch_size": 100, "analysis_window_days": 30}
        return DataAgent("data_001", "DataAgent", config)
    
    def test_data_agent_initialization(self, data_agent):
        """Test data agent initialization."""
        assert data_agent.agent_id == "data_001"
        assert data_agent.name == "DataAgent"
        assert data_agent.status == AgentStatus.IDLE
    
    def test_data_agent_capabilities(self, data_agent):
        """Test data agent capabilities."""
        capabilities = data_agent.get_capabilities()
        
        capability_names = [cap.name for cap in capabilities]
        assert "data_analysis" in capability_names
        assert "statistical_analysis" in capability_names
        assert "anomaly_detection" in capability_names
        assert "trend_analysis" in capability_names
    
    def test_data_agent_analysis(self, data_agent):
        """Test data analysis functionality."""
        # Mock data processor
        mock_processor = Mock()
        mock_processor.df = pd.DataFrame({
            'spend': [100, 200, 150],
            'revenue': [500, 1000, 750],
            'impressions': [1000, 2000, 1500],
            'clicks': [50, 100, 75],
            'ctr': [0.05, 0.05, 0.05],
            'purchases': [5, 10, 7],
            'roas': [5.0, 5.0, 5.0]
        })
        mock_processor.get_data_summary.return_value = {
            'total_records': 3,
            'total_spend': 450,
            'total_revenue': 2250,
            'avg_roas': 5.0
        }
        # Ensure recent performance method returns a dataframe-like object
        mock_processor.get_recent_performance.return_value = mock_processor.df
        
        data_agent.set_data_processor(mock_processor)
        
        task = {
            "task_type": "data_analysis",
            "query": "Analyze ROAS performance",
            "data_summary": {"total_records": 3}
        }
        
        result = asyncio.run(data_agent.execute_task(task))
        
        assert "metrics" in result
        assert "overall" in result["metrics"]


class TestInsightAgent:
    """Test insight agent functionality."""
    
    @pytest.fixture
    def insight_agent(self):
        """Create insight agent for testing."""
        config = {"pattern_min_support": 0.1, "correlation_threshold": 0.7}
        return InsightAgent("insight_001", "InsightAgent", config)
    
    def test_insight_agent_initialization(self, insight_agent):
        """Test insight agent initialization."""
        assert insight_agent.agent_id == "insight_001"
        assert insight_agent.name == "InsightAgent"
        assert insight_agent.status == AgentStatus.IDLE
    
    def test_insight_generation(self, insight_agent):
        """Test insight generation functionality."""
        task = {
            "task_type": "insight_generation",
            "data": {
                "metrics": {
                    "overall": {
                        "avg_roas": 2.5,
                        "avg_ctr": 0.015
                    }
                }
            },
            "query": "Analyze performance"
        }
        
        result = asyncio.run(insight_agent.execute_task(task))
        
        assert "insights" in result
        assert "patterns" in result
        assert "recommendations" in result
        assert "confidence" in result


class TestEvaluatorAgent:
    """Test evaluator agent functionality."""
    
    @pytest.fixture
    def evaluator_agent(self):
        """Create evaluator agent for testing."""
        config = {"validation_threshold": 0.8, "quality_score_weight": 0.6}
        return EvaluatorAgent("evaluator_001", "Evaluator", config)
    
    def test_evaluator_initialization(self, evaluator_agent):
        """Test evaluator agent initialization."""
        assert evaluator_agent.agent_id == "evaluator_001"
        assert evaluator_agent.name == "Evaluator"
        assert evaluator_agent.status == AgentStatus.IDLE
    
    def test_insight_validation(self, evaluator_agent):
        """Test insight validation functionality."""
        task = {
            "task_type": "insight_validation",
            "insights": [
                {
                    "type": "performance",
                    "category": "roas",
                    "insight": "ROAS is below industry average",
                    "confidence": 0.8,
                    "impact": "negative"
                }
            ],
            "data": {
                "metrics": {
                    "overall": {
                        "avg_roas": 2.5
                    }
                }
            }
        }
        
        result = asyncio.run(evaluator_agent.execute_task(task))
        
        assert "validation_results" in result
        assert "confidence_scores" in result
        assert "quality_assessment" in result


class TestCreativeGeneratorAgent:
    """Test creative generator agent functionality."""
    
    @pytest.fixture
    def creative_agent(self):
        """Create creative generator agent for testing."""
        config = {"max_variations": 5, "creativity_score": 0.7}
        return CreativeGeneratorAgent("creative_001", "CreativeGenerator", config)
    
    def test_creative_agent_initialization(self, creative_agent):
        """Test creative agent initialization."""
        assert creative_agent.agent_id == "creative_001"
        assert creative_agent.name == "CreativeGenerator"
        assert creative_agent.status == AgentStatus.IDLE
    
    def test_creative_recommendations(self, creative_agent):
        """Test creative recommendations functionality."""
        task = {
            "task_type": "creative_recommendations",
            "insights": [
                {
                    "type": "performance",
                    "category": "roas",
                    "insight": "ROAS is below target",
                    "impact": "negative"
                }
            ],
            "data": {
                "campaign_analysis": {
                    "campaigns": [
                        {
                            "campaign_name": "Test Campaign",
                            "roas": 2.0,
                            "spend": 1000
                        }
                    ]
                }
            }
        }
        
        result = asyncio.run(creative_agent.execute_task(task))
        
        assert "recommendations" in result
        assert "creative_suggestions" in result
        assert "templates" in result
        assert "priority" in result


class TestReportGenerator:
    """Test report generation functionality."""
    
    @pytest.fixture
    def report_generator(self):
        """Create report generator for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ReportGenerator(temp_dir)
    
    def test_report_generator_initialization(self, report_generator):
        """Test report generator initialization."""
        assert report_generator.output_dir.exists()
    
    def test_report_generation(self, report_generator):
        """Test report generation."""
        analysis_results = {
            "query": "Test Analysis",
            "timestamp": "2025-01-01T00:00:00",
            "summary": {
                "key_findings": ["Finding 1", "Finding 2"],
                "recommendations": ["Recommendation 1"],
                "confidence_level": "high"
            },
            "results": {
                "data_analysis": {
                    "metrics": {
                        "overall": {
                            "total_spend": 1000,
                            "total_revenue": 3000,
                            "avg_roas": 3.0,
                            "avg_ctr": 0.02
                        }
                    }
                },
                "insight_generation": {
                    "insights": [
                        {
                            "type": "performance",
                            "category": "roas",
                            "insight": "ROAS is above average",
                            "confidence": 0.8,
                            "impact": "positive"
                        }
                    ]
                },
                "creative_recommendations": {
                    "recommendations": [
                        {
                            "type": "creative_optimization",
                            "priority": "high",
                            "recommendation": "Optimize creatives",
                            "actions": ["Test new formats"]
                        }
                    ]
                }
            }
        }
        
        report_files = report_generator.generate_report(analysis_results, "Test Query")
        
        assert "markdown" in report_files
        assert "insights" in report_files
        assert "creatives" in report_files
        
        # Check that files were created
        for file_type, file_path in report_files.items():
            assert Path(file_path).exists()


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_analysis(self):
        """Test end-to-end analysis workflow."""
        # This would test the complete workflow from query to report
        # For now, we'll test individual components
        
        # Test configuration loading
        config = Config("config/config.yaml")
        assert config.validate()
        
        # Test data processor with sample data
        sample_data = pd.DataFrame({
            'campaign_name': ['Test Campaign'],
            'date': pd.to_datetime(['2025-01-01']),
            'spend': [100.0],
            'impressions': [1000],
            'clicks': [50],
            'ctr': [0.05],
            'purchases': [5],
            'revenue': [500.0],
            'roas': [5.0],
            'creative_type': ['Image'],
            'audience_type': ['Broad'],
            'platform': ['Facebook'],
            'country': ['US']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            processor = FacebookAdsDataProcessor(f.name)
            summary = processor.get_data_summary()
            
            assert summary['total_records'] == 1
            assert summary['total_spend'] == 100.0
            
            # Clean up
            Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
