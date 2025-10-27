"""
Configuration management for the Agentic Facebook Performance Analyst system.
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the agent system."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration from YAML file."""
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            self._config = yaml.safe_load(file)
        
        # Set environment variables
        self._set_environment_variables()
    
    def _set_environment_variables(self) -> None:
        """Set environment variables from config."""
        if 'data_csv_path' in self._config:
            os.environ['DATA_CSV'] = str(self._config['data_csv_path'])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key with dot notation support."""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.get(f'agents.{agent_name}', {})
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP server configuration."""
        return self.get('mcp_server', {})
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory system configuration."""
        return self.get('memory', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def get_reports_config(self) -> Dict[str, Any]:
        """Get reports configuration."""
        return self.get('reports', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.get('security', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        return self.get('performance', {})
    
    @property
    def python_version(self) -> str:
        """Get required Python version."""
        return self.get('python', '3.10')
    
    @property
    def random_seed(self) -> int:
        """Get random seed for reproducible results."""
        return self.get('random_seed', 42)
    
    @property
    def confidence_min(self) -> float:
        """Get minimum confidence threshold."""
        return self.get('confidence_min', 0.6)
    
    @property
    def data_csv_path(self) -> str:
        """Get data CSV file path."""
        return self.get('data_csv_path', 'data/synthetic_fb_ads_undergarments.csv')
    
    @property
    def use_sample_data(self) -> bool:
        """Check if sample data should be used."""
        return self.get('use_sample_data', False)
    
    def validate(self) -> bool:
        """Validate configuration."""
        required_keys = [
            'python',
            'random_seed',
            'confidence_min',
            'agents',
            'mcp_server',
            'memory',
            'logging',
            'reports'
        ]
        
        for key in required_keys:
            if not self.get(key):
                raise ValueError(f"Missing required configuration key: {key}")
        
        return True


# Global configuration instance
config = Config()
