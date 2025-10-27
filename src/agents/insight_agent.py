"""
Insight Agent - Generates insights and identifies patterns in performance data.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.core.agent_base import BaseAgent, AgentCapability, AgentMessage, MessageType, AgentStatus

logger = logging.getLogger(__name__)


class InsightAgent(BaseAgent):
    """Insight agent responsible for generating insights and identifying patterns."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        """Initialize insight agent."""
        super().__init__(agent_id, name, config)
        self.insight_cache: Dict[str, Any] = {}
        self.pattern_library: Dict[str, Any] = {}
    
    def _initialize_capabilities(self) -> None:
        """Initialize insight agent capabilities."""
        self.capabilities = [
            AgentCapability(
                name="insight_generation",
                description="Generate insights from performance data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "query": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["data"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "insights": {"type": "array"},
                        "patterns": {"type": "array"},
                        "recommendations": {"type": "array"},
                        "confidence": {"type": "number"}
                    }
                },
                required_params=["data"]
            ),
            AgentCapability(
                name="pattern_recognition",
                description="Identify patterns in performance data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "pattern_types": {"type": "array"},
                        "threshold": {"type": "number"}
                    },
                    "required": ["data"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "patterns": {"type": "array"},
                        "pattern_strength": {"type": "object"},
                        "significance": {"type": "object"}
                    }
                },
                required_params=["data"]
            ),
            AgentCapability(
                name="correlation_analysis",
                description="Analyze correlations between different metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "metrics": {"type": "array"},
                        "time_window": {"type": "number"}
                    },
                    "required": ["data", "metrics"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "correlations": {"type": "array"},
                        "causal_relationships": {"type": "array"},
                        "insights": {"type": "array"}
                    }
                },
                required_params=["data", "metrics"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message."""
        try:
            self.update_status(AgentStatus.BUSY)
            
            if message.message_type == MessageType.REQUEST:
                task_type = message.content.get("task_type", "insight_generation")
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
        task_type = task.get("task_type", "insight_generation")
        
        if task_type == "insight_generation":
            return await self._generate_insights(task)
        elif task_type == "pattern_recognition":
            return await self._recognize_patterns(task)
        elif task_type == "correlation_analysis":
            return await self._analyze_correlations(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _generate_insights(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from the data."""
        data = task.get("data", {})
        query = task.get("query", "")
        
        logger.info(f"Generating insights for query: {query}")
        
        insights = []
        patterns = []
        recommendations = []
        
        # Analyze metrics data
        if "metrics" in data:
            insights.extend(await self._analyze_metrics_insights(data["metrics"]))
        
        # Analyze trends data
        if "trends" in data:
            insights.extend(await self._analyze_trend_insights(data["trends"]))
            patterns.extend(await self._identify_trend_patterns(data["trends"]))
        
        # Analyze anomalies
        if "anomalies" in data:
            insights.extend(await self._analyze_anomaly_insights(data["anomalies"]))
        
        # Analyze campaign performance
        if "campaign_analysis" in data:
            insights.extend(await self._analyze_campaign_insights(data["campaign_analysis"]))
            recommendations.extend(await self._generate_campaign_recommendations(data["campaign_analysis"]))
        
        # Analyze audience performance
        if "audience_analysis" in data:
            insights.extend(await self._analyze_audience_insights(data["audience_analysis"]))
            recommendations.extend(await self._generate_audience_recommendations(data["audience_analysis"]))
        
        # Analyze platform performance
        if "platform_analysis" in data:
            insights.extend(await self._analyze_platform_insights(data["platform_analysis"]))
            recommendations.extend(await self._generate_platform_recommendations(data["platform_analysis"]))
        
        # Calculate overall confidence
        confidence = await self._calculate_insight_confidence(insights, patterns)
        
        result = {
            "insights": insights,
            "patterns": patterns,
            "recommendations": recommendations,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache insights
        cache_key = f"insights_{hash(query)}"
        self.insight_cache[cache_key] = result
        
        return result
    
    async def _analyze_metrics_insights(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze metrics to generate insights."""
        insights = []
        
        if "overall" in metrics:
            overall = metrics["overall"]
            
            # ROAS insights
            if overall.get("avg_roas", 0) > 3.0:
                insights.append({
                    "type": "performance",
                    "category": "roas",
                    "insight": "Overall ROAS is above industry average (3.0), indicating strong campaign performance",
                    "confidence": 0.9,
                    "impact": "positive"
                })
            elif overall.get("avg_roas", 0) < 2.0:
                insights.append({
                    "type": "performance",
                    "category": "roas",
                    "insight": "Overall ROAS is below 2.0, indicating potential optimization opportunities",
                    "confidence": 0.8,
                    "impact": "negative"
                })
            
            # CTR insights
            if overall.get("avg_ctr", 0) > 0.02:
                insights.append({
                    "type": "engagement",
                    "category": "ctr",
                    "insight": "CTR is above 2%, indicating strong ad engagement",
                    "confidence": 0.85,
                    "impact": "positive"
                })
            elif overall.get("avg_ctr", 0) < 0.01:
                insights.append({
                    "type": "engagement",
                    "category": "ctr",
                    "insight": "CTR is below 1%, suggesting ad creative or targeting needs improvement",
                    "confidence": 0.8,
                    "impact": "negative"
                })
        
        # Recent performance insights
        if "recent_7_days" in metrics:
            recent = metrics["recent_7_days"]
            overall = metrics.get("overall", {})
            
            if recent.get("avg_roas", 0) < overall.get("avg_roas", 0) * 0.8:
                insights.append({
                    "type": "trend",
                    "category": "performance_decline",
                    "insight": "Recent 7-day ROAS is significantly lower than overall average, indicating performance decline",
                    "confidence": 0.85,
                    "impact": "negative"
                })
        
        return insights
    
    async def _analyze_trend_insights(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze trends to generate insights."""
        insights = []
        
        for metric, trend_data in trends.items():
            change_percent = trend_data.get("change_percent", 0)
            
            if abs(change_percent) > 20:
                direction = "increasing" if change_percent > 0 else "decreasing"
                insights.append({
                    "type": "trend",
                    "category": f"{metric}_trend",
                    "insight": f"{metric.upper()} is {direction} by {abs(change_percent):.1f}% over the past week",
                    "confidence": 0.8,
                    "impact": "positive" if change_percent > 0 else "negative",
                    "magnitude": "high" if abs(change_percent) > 30 else "medium"
                })
            elif abs(change_percent) > 10:
                direction = "increasing" if change_percent > 0 else "decreasing"
                insights.append({
                    "type": "trend",
                    "category": f"{metric}_trend",
                    "insight": f"{metric.upper()} is {direction} by {abs(change_percent):.1f}% over the past week",
                    "confidence": 0.7,
                    "impact": "positive" if change_percent > 0 else "negative",
                    "magnitude": "medium"
                })
        
        return insights
    
    async def _analyze_anomaly_insights(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze anomalies to generate insights."""
        insights = []
        
        if not anomalies:
            return insights
        
        # Group anomalies by type
        high_severity = [a for a in anomalies if a.get("severity") == "high"]
        medium_severity = [a for a in anomalies if a.get("severity") == "medium"]
        
        if high_severity:
            insights.append({
                "type": "anomaly",
                "category": "high_severity",
                "insight": f"Found {len(high_severity)} high-severity anomalies that require immediate attention",
                "confidence": 0.9,
                "impact": "negative",
                "anomalies": high_severity[:3]  # Include top 3
            })
        
        if medium_severity:
            insights.append({
                "type": "anomaly",
                "category": "medium_severity",
                "insight": f"Found {len(medium_severity)} medium-severity anomalies that should be monitored",
                "confidence": 0.7,
                "impact": "neutral",
                "anomalies": medium_severity[:3]  # Include top 3
            })
        
        return insights
    
    async def _analyze_campaign_insights(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze campaign performance to generate insights."""
        insights = []
        
        campaigns = campaign_data.get("campaigns", [])
        if not campaigns:
            return insights
        
        # Find best and worst performers
        best_performer = campaign_data.get("top_performer")
        worst_performer = campaign_data.get("worst_performer")
        
        if best_performer and worst_performer:
            roas_difference = best_performer["roas"] - worst_performer["roas"]
            
            insights.append({
                "type": "campaign_performance",
                "category": "performance_gap",
                "insight": f"Significant performance gap between campaigns: {best_performer['campaign_name']} (ROAS: {best_performer['roas']:.2f}) vs {worst_performer['campaign_name']} (ROAS: {worst_performer['roas']:.2f})",
                "confidence": 0.85,
                "impact": "neutral",
                "gap": roas_difference
            })
        
        # Analyze campaign distribution
        high_performers = [c for c in campaigns if c["roas"] > 3.0]
        low_performers = [c for c in campaigns if c["roas"] < 2.0]
        
        if len(high_performers) > len(campaigns) * 0.5:
            insights.append({
                "type": "campaign_performance",
                "category": "high_performance",
                "insight": f"Most campaigns ({len(high_performers)}/{len(campaigns)}) are performing above ROAS 3.0",
                "confidence": 0.8,
                "impact": "positive"
            })
        elif len(low_performers) > len(campaigns) * 0.5:
            insights.append({
                "type": "campaign_performance",
                "category": "low_performance",
                "insight": f"Most campaigns ({len(low_performers)}/{len(campaigns)}) are performing below ROAS 2.0",
                "confidence": 0.8,
                "impact": "negative"
            })
        
        return insights
    
    async def _analyze_audience_insights(self, audience_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze audience performance to generate insights."""
        insights = []
        
        audiences = audience_data.get("audiences", [])
        if not audiences:
            return insights
        
        best_audience = audience_data.get("best_audience")
        if best_audience:
            insights.append({
                "type": "audience_performance",
                "category": "best_audience",
                "insight": f"{best_audience['audience_type']} audience shows highest ROAS ({best_audience['roas']:.2f})",
                "confidence": 0.9,
                "impact": "positive",
                "audience_type": best_audience["audience_type"]
            })
        
        # Compare audience types
        if len(audiences) > 1:
            roas_values = [a["roas"] for a in audiences]
            roas_variance = max(roas_values) - min(roas_values)
            
            if roas_variance > 2.0:
                insights.append({
                    "type": "audience_performance",
                    "category": "audience_variance",
                    "insight": f"High variance in audience performance (ROAS range: {roas_variance:.2f}), indicating targeting optimization opportunities",
                    "confidence": 0.8,
                    "impact": "neutral",
                    "variance": roas_variance
                })
        
        return insights
    
    async def _analyze_platform_insights(self, platform_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze platform performance to generate insights."""
        insights = []
        
        platforms = platform_data.get("platforms", [])
        if not platforms:
            return insights
        
        best_platform = platform_data.get("best_platform")
        if best_platform:
            insights.append({
                "type": "platform_performance",
                "category": "best_platform",
                "insight": f"{best_platform['platform']} shows highest ROAS ({best_platform['roas']:.2f})",
                "confidence": 0.9,
                "impact": "positive",
                "platform": best_platform["platform"]
            })
        
        # Compare platforms
        if len(platforms) > 1:
            roas_values = [p["roas"] for p in platforms]
            roas_variance = max(roas_values) - min(roas_values)
            
            if roas_variance > 1.0:
                insights.append({
                    "type": "platform_performance",
                    "category": "platform_variance",
                    "insight": f"Significant variance in platform performance (ROAS range: {roas_variance:.2f})",
                    "confidence": 0.8,
                    "impact": "neutral",
                    "variance": roas_variance
                })
        
        return insights
    
    async def _identify_trend_patterns(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns in trend data."""
        patterns = []
        
        # Identify correlation patterns
        trend_values = []
        for metric, trend_data in trends.items():
            trend_values.append({
                "metric": metric,
                "trend": trend_data.get("trend", 0),
                "change_percent": trend_data.get("change_percent", 0)
            })
        
        # Check for correlated trends
        positive_trends = [t for t in trend_values if t["trend"] > 0]
        negative_trends = [t for t in trend_values if t["trend"] < 0]
        
        if len(positive_trends) > 1:
            patterns.append({
                "type": "correlated_trends",
                "pattern": "multiple_positive_trends",
                "description": f"Multiple metrics showing positive trends: {', '.join([t['metric'] for t in positive_trends])}",
                "strength": "medium",
                "metrics": [t["metric"] for t in positive_trends]
            })
        
        if len(negative_trends) > 1:
            patterns.append({
                "type": "correlated_trends",
                "pattern": "multiple_negative_trends",
                "description": f"Multiple metrics showing negative trends: {', '.join([t['metric'] for t in negative_trends])}",
                "strength": "medium",
                "metrics": [t["metric"] for t in negative_trends]
            })
        
        return patterns
    
    async def _generate_campaign_recommendations(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate campaign-specific recommendations."""
        recommendations = []
        
        campaigns = campaign_data.get("campaigns", [])
        if not campaigns:
            return recommendations
        
        # Identify underperforming campaigns
        underperformers = [c for c in campaigns if c["roas"] < 2.0]
        
        if underperformers:
            recommendations.append({
                "type": "campaign_optimization",
                "priority": "high",
                "recommendation": f"Optimize {len(underperformers)} underperforming campaigns with ROAS < 2.0",
                "action": "Review creative, targeting, and bidding strategies",
                "expected_impact": "medium"
            })
        
        # Identify top performers for scaling
        top_performers = [c for c in campaigns if c["roas"] > 4.0]
        
        if top_performers:
            recommendations.append({
                "type": "campaign_scaling",
                "priority": "medium",
                "recommendation": f"Consider scaling {len(top_performers)} high-performing campaigns",
                "action": "Increase budget allocation for top performers",
                "expected_impact": "high"
            })
        
        return recommendations
    
    async def _generate_audience_recommendations(self, audience_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate audience-specific recommendations."""
        recommendations = []
        
        audiences = audience_data.get("audiences", [])
        if not audiences:
            return recommendations
        
        best_audience = audience_data.get("best_audience")
        if best_audience:
            recommendations.append({
                "type": "audience_optimization",
                "priority": "high",
                "recommendation": f"Focus budget on {best_audience['audience_type']} audience (ROAS: {best_audience['roas']:.2f})",
                "action": "Increase budget allocation and create similar audiences",
                "expected_impact": "high"
            })
        
        return recommendations
    
    async def _generate_platform_recommendations(self, platform_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate platform-specific recommendations."""
        recommendations = []
        
        platforms = platform_data.get("platforms", [])
        if not platforms:
            return recommendations
        
        best_platform = platform_data.get("best_platform")
        if best_platform:
            recommendations.append({
                "type": "platform_optimization",
                "priority": "medium",
                "recommendation": f"Optimize for {best_platform['platform']} platform (ROAS: {best_platform['roas']:.2f})",
                "action": "Adjust creative formats and messaging for platform",
                "expected_impact": "medium"
            })
        
        return recommendations
    
    async def _calculate_insight_confidence(self, insights: List[Dict[str, Any]], patterns: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in insights."""
        if not insights:
            return 0.0
        
        # Calculate weighted average confidence
        total_confidence = sum(insight.get("confidence", 0.5) for insight in insights)
        avg_confidence = total_confidence / len(insights)
        
        # Adjust based on pattern strength
        if patterns:
            pattern_strength = sum(pattern.get("strength", "low") == "high" for pattern in patterns)
            pattern_bonus = min(pattern_strength * 0.05, 0.1)  # Max 10% bonus
            avg_confidence += pattern_bonus
        
        return min(avg_confidence, 1.0)
    
    async def _recognize_patterns(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize patterns in the data."""
        data = task.get("data", {})
        pattern_types = task.get("pattern_types", ["trend", "seasonal", "correlation"])
        threshold = task.get("threshold", 0.7)
        
        patterns = []
        
        # This is a simplified pattern recognition
        # In a real implementation, this would use more sophisticated algorithms
        
        for pattern_type in pattern_types:
            if pattern_type == "trend" and "trends" in data:
                patterns.extend(await self._identify_trend_patterns(data["trends"]))
            elif pattern_type == "correlation" and "metrics" in data:
                patterns.extend(await self._identify_correlation_patterns(data["metrics"]))
        
        return {
            "patterns": patterns,
            "pattern_strength": {p["pattern"]: p["strength"] for p in patterns},
            "significance": {p["pattern"]: "high" if p["strength"] == "high" else "medium" for p in patterns}
        }
    
    async def _identify_correlation_patterns(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify correlation patterns in metrics."""
        patterns = []
        
        # This is a placeholder for correlation pattern identification
        # In a real implementation, this would analyze actual correlations
        
        return patterns
    
    async def _analyze_correlations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations between metrics."""
        data = task.get("data", {})
        metrics = task.get("metrics", [])
        time_window = task.get("time_window", 7)
        
        # This is a placeholder for correlation analysis
        # In a real implementation, this would perform statistical correlation analysis
        
        return {
            "correlations": [],
            "causal_relationships": [],
            "insights": []
        }
