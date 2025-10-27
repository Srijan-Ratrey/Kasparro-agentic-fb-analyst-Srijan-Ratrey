"""
Data Agent - Handles data processing, analysis, and statistical computations.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from src.core.agent_base import BaseAgent, AgentCapability, AgentMessage, MessageType, AgentStatus
from src.utils.data_processor import FacebookAdsDataProcessor

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """Data agent responsible for data processing and statistical analysis."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        """Initialize data agent."""
        super().__init__(agent_id, name, config)
        self.data_processor: Optional[FacebookAdsDataProcessor] = None
        self.analysis_cache: Dict[str, Any] = {}
    
    def _initialize_capabilities(self) -> None:
        """Initialize data agent capabilities."""
        self.capabilities = [
            AgentCapability(
                name="data_analysis",
                description="Analyze Facebook ads performance data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "data_summary": {"type": "object"},
                        "time_range": {"type": "string"},
                        "metrics": {"type": "array"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "metrics": {"type": "object"},
                        "trends": {"type": "object"},
                        "anomalies": {"type": "array"},
                        "summary": {"type": "object"}
                    }
                },
                required_params=["query"]
            ),
            AgentCapability(
                name="statistical_analysis",
                description="Perform statistical analysis on performance metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "analysis_type": {"type": "string"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["data", "analysis_type"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "object"},
                        "statistics": {"type": "object"},
                        "significance": {"type": "object"}
                    }
                },
                required_params=["data", "analysis_type"]
            ),
            AgentCapability(
                name="anomaly_detection",
                description="Detect anomalies in performance data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "threshold": {"type": "number"},
                        "method": {"type": "string"}
                    },
                    "required": ["data"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "anomalies": {"type": "array"},
                        "scores": {"type": "object"},
                        "method_used": {"type": "string"}
                    }
                },
                required_params=["data"]
            ),
            AgentCapability(
                name="trend_analysis",
                description="Analyze trends in performance metrics over time",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "metric": {"type": "string"},
                        "window": {"type": "number"}
                    },
                    "required": ["data", "metric"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "trend": {"type": "number"},
                        "change_percent": {"type": "number"},
                        "significance": {"type": "number"},
                        "forecast": {"type": "object"}
                    }
                },
                required_params=["data", "metric"]
            )
        ]
    
    def set_data_processor(self, data_processor: FacebookAdsDataProcessor) -> None:
        """Set the data processor instance."""
        self.data_processor = data_processor
        logger.info("Data processor set for data agent")
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message."""
        try:
            self.update_status(AgentStatus.BUSY)
            
            if message.message_type == MessageType.REQUEST:
                task_type = message.content.get("task_type", "data_analysis")
                result = await self.execute_task(message.content)
            else:
                result = {"status": "acknowledged", "message": "Message received"}
            
            response = AgentMessage(
                message_id=f"response_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender=self.agent_id,
                recipient=message.sender,
                message_type=MessageType.RESPONSE,
                content=result,
                timestamp=datetime.now(),
                correlation_id=message.message_id
            )
            
            self.update_status(AgentStatus.COMPLETED)
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.update_status(AgentStatus.ERROR)
            
            error_response = AgentMessage(
                message_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender=self.agent_id,
                recipient=message.sender,
                message_type=MessageType.ERROR,
                content={"error": str(e), "timestamp": datetime.now().isoformat()},
                timestamp=datetime.now(),
                correlation_id=message.message_id
            )
            return error_response
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task."""
        task_type = task.get("task_type", "data_analysis")
        
        if task_type == "data_analysis":
            return await self._analyze_data(task)
        elif task_type == "statistical_analysis":
            return await self._perform_statistical_analysis(task)
        elif task_type == "anomaly_detection":
            return await self._detect_anomalies(task)
        elif task_type == "trend_analysis":
            return await self._analyze_trends(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _analyze_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Facebook ads data based on the query."""
        if not self.data_processor:
            return {"error": "Data processor not initialized"}
        
        query = task.get("query", "")
        query_lower = query.lower()
        
        logger.info(f"Analyzing data for query: {query}")
        
        # Determine analysis scope based on query
        analysis_results = {}
        
        # Basic metrics analysis
        if any(keyword in query_lower for keyword in ["roas", "revenue", "spend", "performance"]):
            analysis_results["metrics"] = await self._get_performance_metrics()
        
        # Trend analysis
        if any(keyword in query_lower for keyword in ["trend", "change", "over time", "recent"]):
            analysis_results["trends"] = await self._get_trend_analysis()
        
        # Anomaly detection
        if any(keyword in query_lower for keyword in ["anomaly", "unusual", "spike", "drop"]):
            analysis_results["anomalies"] = await self._get_anomaly_analysis()
        
        # Campaign-specific analysis
        if any(keyword in query_lower for keyword in ["campaign", "adset", "creative"]):
            analysis_results["campaign_analysis"] = await self._get_campaign_analysis()
        
        # Audience analysis
        if any(keyword in query_lower for keyword in ["audience", "targeting", "demographic"]):
            analysis_results["audience_analysis"] = await self._get_audience_analysis()
        
        # Platform analysis
        if any(keyword in query_lower for keyword in ["platform", "facebook", "instagram"]):
            analysis_results["platform_analysis"] = await self._get_platform_analysis()
        
        # Store results in cache
        cache_key = f"analysis_{hash(query)}"
        self.analysis_cache[cache_key] = analysis_results
        
        return analysis_results
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics."""
        if not self.data_processor:
            return {}
        
        df = self.data_processor.df
        
        return {
            "overall": {
                "total_spend": float(df['spend'].sum()),
                "total_revenue": float(df['revenue'].sum()),
                "total_impressions": int(df['impressions'].sum()),
                "total_clicks": int(df['clicks'].sum()),
                "total_purchases": int(df['purchases'].sum()),
                "avg_roas": float(df['roas'].mean()),
                "avg_ctr": float(df['ctr'].mean()),
                "conversion_rate": float(df['purchases'].sum() / df['clicks'].sum()) if df['clicks'].sum() > 0 else 0
            },
            "recent_7_days": await self._get_recent_metrics(7),
            "recent_30_days": await self._get_recent_metrics(30)
        }
    
    async def _get_recent_metrics(self, days: int) -> Dict[str, Any]:
        """Get metrics for recent days."""
        if not self.data_processor:
            return {}
        
        recent_data = self.data_processor.get_recent_performance(days)
        
        if len(recent_data) == 0:
            return {}
        
        return {
            "spend": float(recent_data['spend'].sum()),
            "revenue": float(recent_data['revenue'].sum()),
            "impressions": int(recent_data['impressions'].sum()),
            "clicks": int(recent_data['clicks'].sum()),
            "purchases": int(recent_data['purchases'].sum()),
            "avg_roas": float(recent_data['roas'].mean()),
            "avg_ctr": float(recent_data['ctr'].mean()),
            "days_analyzed": len(recent_data)
        }
    
    async def _get_trend_analysis(self) -> Dict[str, Any]:
        """Get trend analysis for key metrics."""
        if not self.data_processor:
            return {}
        
        trends = {}
        
        # Analyze ROAS trend
        roas_trend = self.data_processor.calculate_trends('roas', 7)
        trends["roas"] = roas_trend
        
        # Analyze spend trend
        spend_trend = self.data_processor.calculate_trends('spend', 7)
        trends["spend"] = spend_trend
        
        # Analyze revenue trend
        revenue_trend = self.data_processor.calculate_trends('revenue', 7)
        trends["revenue"] = revenue_trend
        
        # Analyze CTR trend
        ctr_trend = self.data_processor.calculate_trends('ctr', 7)
        trends["ctr"] = ctr_trend
        
        return trends
    
    async def _get_anomaly_analysis(self) -> List[Dict[str, Any]]:
        """Get anomaly analysis."""
        if not self.data_processor:
            return []
        
        anomalies = []
        
        # Detect ROAS anomalies
        roas_anomalies = self.data_processor.detect_anomalies('roas', 2.0)
        for _, row in roas_anomalies.iterrows():
            anomalies.append({
                "date": row['date'].strftime('%Y-%m-%d'),
                "metric": "roas",
                "value": float(row['roas']),
                "z_score": float(row['z_score']),
                "campaign": row['campaign_name'],
                "severity": "high" if row['z_score'] > 3 else "medium"
            })
        
        # Detect spend anomalies
        spend_anomalies = self.data_processor.detect_anomalies('spend', 2.0)
        for _, row in spend_anomalies.iterrows():
            anomalies.append({
                "date": row['date'].strftime('%Y-%m-%d'),
                "metric": "spend",
                "value": float(row['spend']),
                "z_score": float(row['z_score']),
                "campaign": row['campaign_name'],
                "severity": "high" if row['z_score'] > 3 else "medium"
            })
        
        # Sort by severity and z_score
        anomalies.sort(key=lambda x: (x['severity'] == 'high', x['z_score']), reverse=True)
        
        return anomalies[:10]  # Return top 10 anomalies
    
    async def _get_campaign_analysis(self) -> Dict[str, Any]:
        """Get campaign performance analysis."""
        if not self.data_processor:
            return {}
        
        campaign_performance = self.data_processor.get_campaign_performance()
        
        # Convert to list of dictionaries for JSON serialization
        campaigns = []
        for _, row in campaign_performance.iterrows():
            campaigns.append({
                "campaign_name": row['campaign_name'],
                "spend": float(row['spend']),
                "revenue": float(row['revenue']),
                "roas": float(row['roas']),
                "ctr": float(row['ctr']),
                "impressions": int(row['impressions']),
                "clicks": int(row['clicks']),
                "purchases": int(row['purchases'])
            })
        
        # Sort by ROAS descending
        campaigns.sort(key=lambda x: x['roas'], reverse=True)
        
        return {
            "campaigns": campaigns,
            "top_performer": campaigns[0] if campaigns else None,
            "worst_performer": campaigns[-1] if campaigns else None,
            "total_campaigns": len(campaigns)
        }
    
    async def _get_audience_analysis(self) -> Dict[str, Any]:
        """Get audience performance analysis."""
        if not self.data_processor:
            return {}
        
        audience_performance = self.data_processor.get_audience_performance()
        
        audiences = []
        for _, row in audience_performance.iterrows():
            audiences.append({
                "audience_type": row['audience_type'],
                "spend": float(row['spend']),
                "revenue": float(row['revenue']),
                "roas": float(row['roas']),
                "ctr": float(row['ctr']),
                "impressions": int(row['impressions']),
                "clicks": int(row['clicks']),
                "purchases": int(row['purchases'])
            })
        
        # Sort by ROAS descending
        audiences.sort(key=lambda x: x['roas'], reverse=True)
        
        return {
            "audiences": audiences,
            "best_audience": audiences[0] if audiences else None,
            "audience_count": len(audiences)
        }
    
    async def _get_platform_analysis(self) -> Dict[str, Any]:
        """Get platform performance analysis."""
        if not self.data_processor:
            return {}
        
        platform_performance = self.data_processor.get_platform_performance()
        
        platforms = []
        for _, row in platform_performance.iterrows():
            platforms.append({
                "platform": row['platform'],
                "spend": float(row['spend']),
                "revenue": float(row['revenue']),
                "roas": float(row['roas']),
                "ctr": float(row['ctr']),
                "impressions": int(row['impressions']),
                "clicks": int(row['clicks']),
                "purchases": int(row['purchases'])
            })
        
        # Sort by ROAS descending
        platforms.sort(key=lambda x: x['roas'], reverse=True)
        
        return {
            "platforms": platforms,
            "best_platform": platforms[0] if platforms else None,
            "platform_count": len(platforms)
        }
    
    async def _perform_statistical_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on the data."""
        analysis_type = task.get("analysis_type", "correlation")
        parameters = task.get("parameters", {})
        
        if not self.data_processor:
            return {"error": "Data processor not initialized"}
        
        df = self.data_processor.df
        
        if analysis_type == "correlation":
            # Calculate correlation matrix for numeric columns
            numeric_columns = ['spend', 'impressions', 'clicks', 'ctr', 'purchases', 'revenue', 'roas']
            correlation_matrix = df[numeric_columns].corr()
            
            return {
                "correlation_matrix": correlation_matrix.to_dict(),
                "strong_correlations": self._find_strong_correlations(correlation_matrix),
                "analysis_type": "correlation"
            }
        
        elif analysis_type == "regression":
            # Simple linear regression analysis
            from sklearn.linear_model import LinearRegression
            
            X = df[['spend', 'impressions', 'clicks']].fillna(0)
            y = df['revenue'].fillna(0)
            
            model = LinearRegression()
            model.fit(X, y)
            
            return {
                "coefficients": model.coef_.tolist(),
                "intercept": float(model.intercept_),
                "r_squared": float(model.score(X, y)),
                "analysis_type": "regression"
            }
        
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
    
    def _find_strong_correlations(self, correlation_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations in the correlation matrix."""
        strong_correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_correlations.append({
                        "variable1": correlation_matrix.columns[i],
                        "variable2": correlation_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong" if abs(corr_value) >= 0.8 else "moderate"
                    })
        
        return strong_correlations
    
    async def _detect_anomalies(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using specified method."""
        threshold = task.get("threshold", 2.0)
        method = task.get("method", "z_score")
        
        if not self.data_processor:
            return {"error": "Data processor not initialized"}
        
        if method == "z_score":
            anomalies = self.data_processor.detect_anomalies('roas', threshold)
            
            anomaly_list = []
            for _, row in anomalies.iterrows():
                anomaly_list.append({
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "campaign": row['campaign_name'],
                    "metric": "roas",
                    "value": float(row['roas']),
                    "z_score": float(row['z_score']),
                    "severity": "high" if row['z_score'] > 3 else "medium"
                })
            
            return {
                "anomalies": anomaly_list,
                "method_used": "z_score",
                "threshold": threshold,
                "total_anomalies": len(anomaly_list)
            }
        
        else:
            return {"error": f"Unknown anomaly detection method: {method}"}
    
    async def _analyze_trends(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends for a specific metric."""
        metric = task.get("metric", "roas")
        window = task.get("window", 7)
        
        if not self.data_processor:
            return {"error": "Data processor not initialized"}
        
        trend_data = self.data_processor.calculate_trends(metric, window)
        
        return {
            "metric": metric,
            "trend": trend_data.get("trend", 0),
            "change_percent": trend_data.get("change_percent", 0),
            "current_value": trend_data.get("current_value", 0),
            "previous_value": trend_data.get("previous_value", 0),
            "window_days": window,
            "significance": "high" if abs(trend_data.get("change_percent", 0)) > 20 else "medium" if abs(trend_data.get("change_percent", 0)) > 10 else "low"
        }
