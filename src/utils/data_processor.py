"""
Data processing utilities for Facebook ads analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FacebookAdsDataProcessor:
    """Processes Facebook ads data for analysis."""
    
    def __init__(self, csv_path: str):
        """Initialize with CSV file path."""
        self.csv_path = Path(csv_path)
        self.df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from CSV file."""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} records from {self.csv_path}")
            self._clean_data()
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def _clean_data(self) -> None:
        """Clean and preprocess the data."""
        if self.df is None:
            return
        
        # Convert date column to datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Handle missing values in spend column
        self.df['spend'] = pd.to_numeric(self.df['spend'], errors='coerce').fillna(0)
        
        # Ensure numeric columns are properly typed
        numeric_columns = ['spend', 'impressions', 'clicks', 'ctr', 'purchases', 'revenue', 'roas']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Clean campaign names (remove extra spaces)
        self.df['campaign_name'] = self.df['campaign_name'].str.strip()
        
        logger.info("Data cleaning completed")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the data."""
        if self.df is None:
            return {}
        
        return {
            'total_records': len(self.df),
            'date_range': {
                'start': self.df['date'].min().strftime('%Y-%m-%d'),
                'end': self.df['date'].max().strftime('%Y-%m-%d')
            },
            'campaigns': self.df['campaign_name'].nunique(),
            'total_spend': self.df['spend'].sum(),
            'total_revenue': self.df['revenue'].sum(),
            'avg_roas': self.df['roas'].mean(),
            'platforms': self.df['platform'].value_counts().to_dict(),
            'countries': self.df['country'].value_counts().to_dict(),
            'creative_types': self.df['creative_type'].value_counts().to_dict()
        }
    
    def get_time_series_data(self, metric: str = 'roas', 
                           group_by: Optional[str] = None) -> pd.DataFrame:
        """Get time series data for analysis."""
        if self.df is None:
            return pd.DataFrame()
        
        if group_by:
            return self.df.groupby(['date', group_by])[metric].mean().reset_index()
        else:
            return self.df.groupby('date')[metric].mean().reset_index()
    
    def get_campaign_performance(self, campaign_name: Optional[str] = None) -> pd.DataFrame:
        """Get campaign performance metrics."""
        if self.df is None:
            return pd.DataFrame()
        
        if campaign_name:
            campaign_data = self.df[self.df['campaign_name'] == campaign_name]
        else:
            campaign_data = self.df
        
        return campaign_data.groupby('campaign_name').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'purchases': 'sum',
            'revenue': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).reset_index()
    
    def detect_anomalies(self, metric: str = 'roas', threshold: float = 2.0) -> pd.DataFrame:
        """Detect anomalies in the data using statistical methods."""
        if self.df is None:
            return pd.DataFrame()
        
        # Calculate z-scores
        metric_data = self.df[metric].dropna()
        z_scores = np.abs((metric_data - metric_data.mean()) / metric_data.std())
        
        # Identify anomalies
        anomalies = self.df[z_scores > threshold].copy()
        anomalies['z_score'] = z_scores[z_scores > threshold]
        
        return anomalies.sort_values('z_score', ascending=False)
    
    def get_creative_performance(self) -> pd.DataFrame:
        """Analyze performance by creative type."""
        if self.df is None:
            return pd.DataFrame()
        
        return self.df.groupby('creative_type').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'purchases': 'sum',
            'revenue': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).reset_index()
    
    def get_audience_performance(self) -> pd.DataFrame:
        """Analyze performance by audience type."""
        if self.df is None:
            return pd.DataFrame()
        
        return self.df.groupby('audience_type').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'purchases': 'sum',
            'revenue': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).reset_index()
    
    def get_platform_performance(self) -> pd.DataFrame:
        """Analyze performance by platform."""
        if self.df is None:
            return pd.DataFrame()
        
        return self.df.groupby('platform').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'purchases': 'sum',
            'revenue': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).reset_index()
    
    def get_recent_performance(self, days: int = 7) -> pd.DataFrame:
        """Get performance data for recent days."""
        if self.df is None:
            return pd.DataFrame()
        
        cutoff_date = self.df['date'].max() - timedelta(days=days)
        return self.df[self.df['date'] >= cutoff_date]
    
    def calculate_trends(self, metric: str = 'roas', window: int = 7) -> Dict[str, float]:
        """Calculate trend metrics."""
        if self.df is None:
            return {}
        
        # Get recent data
        recent_data = self.get_recent_performance(window)
        
        if len(recent_data) < 2:
            return {'trend': 0.0, 'change_percent': 0.0}
        
        # Calculate trend
        time_series = recent_data.groupby('date')[metric].mean().sort_index()
        
        if len(time_series) < 2:
            return {'trend': 0.0, 'change_percent': 0.0}
        
        # Simple linear trend calculation
        x = np.arange(len(time_series))
        y = time_series.values
        
        if len(x) > 1:
            trend = np.polyfit(x, y, 1)[0]
            change_percent = ((time_series.iloc[-1] - time_series.iloc[0]) / time_series.iloc[0]) * 100
        else:
            trend = 0.0
            change_percent = 0.0
        
        return {
            'trend': trend,
            'change_percent': change_percent,
            'current_value': time_series.iloc[-1],
            'previous_value': time_series.iloc[0]
        }
    
    def export_sample_data(self, sample_size: int = 1000, output_path: str = "data/sample_fb_ads.csv") -> None:
        """Export a sample of the data for testing."""
        if self.df is None:
            return
        
        sample_df = self.df.sample(n=min(sample_size, len(self.df)), random_state=42)
        sample_df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(sample_df)} records to {output_path}")
