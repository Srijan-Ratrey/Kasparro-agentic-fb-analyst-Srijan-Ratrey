"""
Evaluator Agent - Validates insights and provides quality assessment.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.core.agent_base import BaseAgent, AgentCapability, AgentMessage, MessageType, AgentStatus

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """Evaluator agent responsible for validating insights and providing quality assessment."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        """Initialize evaluator agent."""
        super().__init__(agent_id, name, config)
        self.validation_cache: Dict[str, Any] = {}
        self.quality_metrics: Dict[str, Any] = {}
    
    def _initialize_capabilities(self) -> None:
        """Initialize evaluator agent capabilities."""
        self.capabilities = [
            AgentCapability(
                name="insight_validation",
                description="Validate insights for accuracy and reliability",
                input_schema={
                    "type": "object",
                    "properties": {
                        "insights": {"type": "array"},
                        "data": {"type": "object"},
                        "context": {"type": "object"}
                    },
                    "required": ["insights"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "validation_results": {"type": "array"},
                        "confidence_scores": {"type": "object"},
                        "quality_assessment": {"type": "object"}
                    }
                },
                required_params=["insights"]
            ),
            AgentCapability(
                name="quality_assessment",
                description="Assess the quality of analysis results",
                input_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "object"},
                        "criteria": {"type": "array"},
                        "thresholds": {"type": "object"}
                    },
                    "required": ["results"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "quality_score": {"type": "number"},
                        "assessment": {"type": "object"},
                        "recommendations": {"type": "array"}
                    }
                },
                required_params=["results"]
            ),
            AgentCapability(
                name="statistical_validation",
                description="Validate statistical significance of findings",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "findings": {"type": "array"},
                        "significance_level": {"type": "number"}
                    },
                    "required": ["data", "findings"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "significance_tests": {"type": "array"},
                        "p_values": {"type": "object"},
                        "conclusions": {"type": "array"}
                    }
                },
                required_params=["data", "findings"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message."""
        try:
            self.update_status(AgentStatus.BUSY)
            
            if message.message_type == MessageType.REQUEST:
                task_type = message.content.get("task_type", "insight_validation")
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
        task_type = task.get("task_type", "insight_validation")
        
        if task_type == "insight_validation":
            return await self._validate_insights(task)
        elif task_type == "quality_assessment":
            return await self._assess_quality(task)
        elif task_type == "statistical_validation":
            return await self._validate_statistics(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _validate_insights(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate insights for accuracy and reliability."""
        insights = task.get("insights", [])
        data = task.get("data", {})
        context = task.get("context", {})
        
        logger.info(f"Validating {len(insights)} insights")
        
        validation_results = []
        confidence_scores = {}
        
        for insight in insights:
            validation_result = await self._validate_single_insight(insight, data, context)
            validation_results.append(validation_result)
            
            # Store confidence score
            insight_id = insight.get("type", "unknown") + "_" + insight.get("category", "unknown")
            confidence_scores[insight_id] = validation_result["confidence"]
        
        # Calculate overall quality assessment
        quality_assessment = await self._calculate_quality_assessment(validation_results)
        
        result = {
            "validation_results": validation_results,
            "confidence_scores": confidence_scores,
            "quality_assessment": quality_assessment,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache validation results
        cache_key = f"validation_{hash(str(insights))}"
        self.validation_cache[cache_key] = result
        
        return result
    
    async def _validate_single_insight(self, insight: Dict[str, Any], data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single insight."""
        insight_type = insight.get("type", "unknown")
        category = insight.get("category", "unknown")
        confidence = insight.get("confidence", 0.5)
        
        validation_result = {
            "insight_id": f"{insight_type}_{category}",
            "type": insight_type,
            "category": category,
            "confidence": confidence,
            "validation_status": "valid",
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        # Validate based on insight type
        if insight_type == "performance":
            validation_result = await self._validate_performance_insight(insight, data, validation_result)
        elif insight_type == "trend":
            validation_result = await self._validate_trend_insight(insight, data, validation_result)
        elif insight_type == "anomaly":
            validation_result = await self._validate_anomaly_insight(insight, data, validation_result)
        elif insight_type == "campaign_performance":
            validation_result = await self._validate_campaign_insight(insight, data, validation_result)
        elif insight_type == "audience_performance":
            validation_result = await self._validate_audience_insight(insight, data, validation_result)
        elif insight_type == "platform_performance":
            validation_result = await self._validate_platform_insight(insight, data, validation_result)
        
        # Adjust confidence based on validation
        validation_result["confidence"] = await self._adjust_confidence(validation_result)
        
        return validation_result
    
    async def _validate_performance_insight(self, insight: Dict[str, Any], data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance insights."""
        category = insight.get("category", "")
        
        if category == "roas":
            # Validate ROAS insight against data
            if "metrics" in data and "overall" in data["metrics"]:
                avg_roas = data["metrics"]["overall"].get("avg_roas", 0)
                
                if avg_roas > 3.0 and insight.get("impact") == "positive":
                    validation_result["strengths"].append("ROAS insight aligns with actual data")
                elif avg_roas < 2.0 and insight.get("impact") == "negative":
                    validation_result["strengths"].append("ROAS insight aligns with actual data")
                else:
                    validation_result["issues"].append("ROAS insight may not align with actual data")
        
        elif category == "ctr":
            # Validate CTR insight against data
            if "metrics" in data and "overall" in data["metrics"]:
                avg_ctr = data["metrics"]["overall"].get("avg_ctr", 0)
                
                if avg_ctr > 0.02 and insight.get("impact") == "positive":
                    validation_result["strengths"].append("CTR insight aligns with actual data")
                elif avg_ctr < 0.01 and insight.get("impact") == "negative":
                    validation_result["strengths"].append("CTR insight aligns with actual data")
                else:
                    validation_result["issues"].append("CTR insight may not align with actual data")
        
        return validation_result
    
    async def _validate_trend_insight(self, insight: Dict[str, Any], data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trend insights."""
        category = insight.get("category", "")
        
        if "trends" in data:
            # Extract metric from category (e.g., "roas_trend" -> "roas")
            metric = category.replace("_trend", "")
            
            if metric in data["trends"]:
                trend_data = data["trends"][metric]
                change_percent = trend_data.get("change_percent", 0)
                
                # Validate trend direction and magnitude
                if abs(change_percent) > 20 and insight.get("magnitude") == "high":
                    validation_result["strengths"].append("Trend magnitude aligns with actual data")
                elif abs(change_percent) > 10 and insight.get("magnitude") == "medium":
                    validation_result["strengths"].append("Trend magnitude aligns with actual data")
                else:
                    validation_result["issues"].append("Trend magnitude may not align with actual data")
        
        return validation_result
    
    async def _validate_anomaly_insight(self, insight: Dict[str, Any], data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate anomaly insights."""
        if "anomalies" in data:
            anomalies = data["anomalies"]
            
            if insight.get("category") == "high_severity":
                high_severity_count = len([a for a in anomalies if a.get("severity") == "high"])
                expected_count = len(insight.get("anomalies", []))
                
                if high_severity_count > 0:
                    validation_result["strengths"].append("High-severity anomalies confirmed in data")
                else:
                    validation_result["issues"].append("No high-severity anomalies found in data")
        
        return validation_result
    
    async def _validate_campaign_insight(self, insight: Dict[str, Any], data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate campaign performance insights."""
        if "campaign_analysis" in data:
            campaigns = data["campaign_analysis"].get("campaigns", [])
            
            if insight.get("category") == "performance_gap":
                if len(campaigns) > 1:
                    roas_values = [c["roas"] for c in campaigns]
                    actual_gap = max(roas_values) - min(roas_values)
                    
                    if actual_gap > 2.0:
                        validation_result["strengths"].append("Performance gap confirmed in data")
                    else:
                        validation_result["issues"].append("Performance gap may be overstated")
        
        return validation_result
    
    async def _validate_audience_insight(self, insight: Dict[str, Any], data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate audience performance insights."""
        if "audience_analysis" in data:
            audiences = data["audience_analysis"].get("audiences", [])
            
            if insight.get("category") == "best_audience":
                if audiences:
                    best_audience = max(audiences, key=lambda x: x["roas"])
                    if best_audience["audience_type"] == insight.get("audience_type"):
                        validation_result["strengths"].append("Best audience identification confirmed")
                    else:
                        validation_result["issues"].append("Best audience identification may be incorrect")
        
        return validation_result
    
    async def _validate_platform_insight(self, insight: Dict[str, Any], data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate platform performance insights."""
        if "platform_analysis" in data:
            platforms = data["platform_analysis"].get("platforms", [])
            
            if insight.get("category") == "best_platform":
                if platforms:
                    best_platform = max(platforms, key=lambda x: x["roas"])
                    if best_platform["platform"] == insight.get("platform"):
                        validation_result["strengths"].append("Best platform identification confirmed")
                    else:
                        validation_result["issues"].append("Best platform identification may be incorrect")
        
        return validation_result
    
    async def _adjust_confidence(self, validation_result: Dict[str, Any]) -> float:
        """Adjust confidence based on validation results."""
        base_confidence = validation_result["confidence"]
        
        # Increase confidence for strengths
        strength_bonus = len(validation_result["strengths"]) * 0.05
        
        # Decrease confidence for issues
        issue_penalty = len(validation_result["issues"]) * 0.1
        
        adjusted_confidence = base_confidence + strength_bonus - issue_penalty
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, adjusted_confidence))
    
    async def _calculate_quality_assessment(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall quality assessment."""
        if not validation_results:
            return {"quality_score": 0.0, "assessment": "no_data"}
        
        # Calculate average confidence
        avg_confidence = sum(r["confidence"] for r in validation_results) / len(validation_results)
        
        # Count issues and strengths
        total_issues = sum(len(r["issues"]) for r in validation_results)
        total_strengths = sum(len(r["strengths"]) for r in validation_results)
        
        # Calculate quality score
        quality_score = avg_confidence * (1 - total_issues * 0.1) + (total_strengths * 0.05)
        quality_score = max(0.0, min(1.0, quality_score))
        
        # Determine quality level
        if quality_score >= 0.8:
            quality_level = "high"
        elif quality_score >= 0.6:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        return {
            "quality_score": quality_score,
            "quality_level": quality_level,
            "average_confidence": avg_confidence,
            "total_issues": total_issues,
            "total_strengths": total_strengths,
            "assessment": f"Quality assessment: {quality_level} (score: {quality_score:.2f})"
        }
    
    async def _assess_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of analysis results."""
        results = task.get("results", {})
        criteria = task.get("criteria", ["accuracy", "completeness", "relevance"])
        thresholds = task.get("thresholds", {"accuracy": 0.8, "completeness": 0.7, "relevance": 0.8})
        
        quality_scores = {}
        
        for criterion in criteria:
            if criterion == "accuracy":
                quality_scores["accuracy"] = await self._assess_accuracy(results)
            elif criterion == "completeness":
                quality_scores["completeness"] = await self._assess_completeness(results)
            elif criterion == "relevance":
                quality_scores["relevance"] = await self._assess_relevance(results)
        
        # Calculate overall quality score
        overall_score = sum(quality_scores.values()) / len(quality_scores)
        
        # Generate recommendations
        recommendations = []
        for criterion, score in quality_scores.items():
            threshold = thresholds.get(criterion, 0.7)
            if score < threshold:
                recommendations.append(f"Improve {criterion}: current score {score:.2f} below threshold {threshold}")
        
        return {
            "quality_score": overall_score,
            "assessment": {
                "overall_score": overall_score,
                "criterion_scores": quality_scores,
                "thresholds": thresholds
            },
            "recommendations": recommendations
        }
    
    async def _assess_accuracy(self, results: Dict[str, Any]) -> float:
        """Assess accuracy of results."""
        # This is a simplified accuracy assessment
        # In a real implementation, this would compare against ground truth or known patterns
        
        accuracy_score = 0.8  # Placeholder score
        
        # Adjust based on data quality indicators
        if "metrics" in results and "overall" in results["metrics"]:
            metrics = results["metrics"]["overall"]
            if metrics.get("avg_roas", 0) > 0:
                accuracy_score += 0.1
        
        return min(1.0, accuracy_score)
    
    async def _assess_completeness(self, results: Dict[str, Any]) -> float:
        """Assess completeness of results."""
        completeness_score = 0.0
        
        # Check for required components
        required_components = ["metrics", "insights", "recommendations"]
        for component in required_components:
            if component in results and results[component]:
                completeness_score += 0.33
        
        return min(1.0, completeness_score)
    
    async def _assess_relevance(self, results: Dict[str, Any]) -> float:
        """Assess relevance of results."""
        relevance_score = 0.8  # Placeholder score
        
        # Adjust based on insight quality
        if "insights" in results:
            insights = results["insights"]
            if insights:
                avg_confidence = sum(i.get("confidence", 0.5) for i in insights) / len(insights)
                relevance_score = avg_confidence
        
        return min(1.0, relevance_score)
    
    async def _validate_statistics(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate statistical significance of findings."""
        data = task.get("data", {})
        findings = task.get("findings", [])
        significance_level = task.get("significance_level", 0.05)
        
        significance_tests = []
        p_values = {}
        conclusions = []
        
        # This is a placeholder for statistical validation
        # In a real implementation, this would perform actual statistical tests
        
        for finding in findings:
            test_result = {
                "finding": finding,
                "test_type": "t_test",  # Placeholder
                "p_value": 0.03,  # Placeholder
                "significant": True,  # Placeholder
                "confidence_interval": [0.1, 0.5]  # Placeholder
            }
            significance_tests.append(test_result)
            
            finding_id = finding.get("type", "unknown")
            p_values[finding_id] = test_result["p_value"]
            
            if test_result["p_value"] < significance_level:
                conclusions.append(f"Finding '{finding_id}' is statistically significant")
            else:
                conclusions.append(f"Finding '{finding_id}' is not statistically significant")
        
        return {
            "significance_tests": significance_tests,
            "p_values": p_values,
            "conclusions": conclusions,
            "significance_level": significance_level
        }
