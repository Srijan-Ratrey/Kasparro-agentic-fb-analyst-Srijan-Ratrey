"""
Creative Generator Agent - Generates creative recommendations and content suggestions.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import random

from src.core.agent_base import BaseAgent, AgentCapability, AgentMessage, MessageType, AgentStatus

logger = logging.getLogger(__name__)


class CreativeGeneratorAgent(BaseAgent):
    """Creative generator agent responsible for generating creative recommendations and content suggestions."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        """Initialize creative generator agent."""
        super().__init__(agent_id, name, config)
        self.creative_library: Dict[str, Any] = {}
        self.template_library: Dict[str, Any] = {}
        self.performance_history: Dict[str, Any] = {}
    
    def _initialize_capabilities(self) -> None:
        """Initialize creative generator agent capabilities."""
        self.capabilities = [
            AgentCapability(
                name="creative_recommendations",
                description="Generate creative recommendations based on performance data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "insights": {"type": "array"},
                        "data": {"type": "object"},
                        "constraints": {"type": "object"}
                    },
                    "required": ["insights"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "recommendations": {"type": "array"},
                        "creative_suggestions": {"type": "array"},
                        "templates": {"type": "array"},
                        "priority": {"type": "object"}
                    }
                },
                required_params=["insights"]
            ),
            AgentCapability(
                name="content_generation",
                description="Generate specific content for ads",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "target_audience": {"type": "string"},
                        "platform": {"type": "string"},
                        "requirements": {"type": "object"}
                    },
                    "required": ["content_type", "target_audience"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "array"},
                        "variations": {"type": "array"},
                        "guidelines": {"type": "array"}
                    }
                },
                required_params=["content_type", "target_audience"]
            ),
            AgentCapability(
                name="a_b_testing_suggestions",
                description="Suggest A/B testing strategies for creatives",
                input_schema={
                    "type": "object",
                    "properties": {
                        "current_performance": {"type": "object"},
                        "test_objectives": {"type": "array"},
                        "budget_constraints": {"type": "object"}
                    },
                    "required": ["current_performance"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "test_plans": {"type": "array"},
                        "hypotheses": {"type": "array"},
                        "success_metrics": {"type": "array"}
                    }
                },
                required_params=["current_performance"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message."""
        try:
            self.update_status(AgentStatus.BUSY)
            
            if message.message_type == MessageType.REQUEST:
                task_type = message.content.get("task_type", "creative_recommendations")
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
        task_type = task.get("task_type", "creative_recommendations")
        
        if task_type == "creative_recommendations":
            return await self._generate_creative_recommendations(task)
        elif task_type == "content_generation":
            return await self._generate_content(task)
        elif task_type == "a_b_testing_suggestions":
            return await self._suggest_ab_tests(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _generate_creative_recommendations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative recommendations based on insights."""
        insights = task.get("insights", [])
        data = task.get("data", {})
        constraints = task.get("constraints", {})
        
        logger.info(f"Generating creative recommendations for {len(insights)} insights")
        
        recommendations = []
        creative_suggestions = []
        templates = []
        
        # Analyze insights to generate recommendations
        for insight in insights:
            insight_type = insight.get("type", "")
            category = insight.get("category", "")
            impact = insight.get("impact", "neutral")
            
            if insight_type == "performance" and impact == "negative":
                recommendations.extend(await self._generate_performance_recommendations(insight, data))
            elif insight_type == "trend" and impact == "negative":
                recommendations.extend(await self._generate_trend_recommendations(insight, data))
            elif insight_type == "campaign_performance":
                recommendations.extend(await self._generate_campaign_recommendations(insight, data))
            elif insight_type == "audience_performance":
                recommendations.extend(await self._generate_audience_recommendations(insight, data))
            elif insight_type == "platform_performance":
                recommendations.extend(await self._generate_platform_recommendations(insight, data))
        
        # Generate creative suggestions based on data
        if "campaign_analysis" in data:
            creative_suggestions.extend(await self._generate_creative_suggestions(data["campaign_analysis"]))
        
        if "audience_analysis" in data:
            creative_suggestions.extend(await self._generate_audience_creative_suggestions(data["audience_analysis"]))
        
        if "platform_analysis" in data:
            creative_suggestions.extend(await self._generate_platform_creative_suggestions(data["platform_analysis"]))
        
        # Generate templates
        templates = await self._generate_templates(data)
        
        # Prioritize recommendations
        priority = await self._prioritize_recommendations(recommendations, creative_suggestions)
        # Enrich high-priority recommendations with supporting metrics and A/B test plans
        for rec in recommendations:
            try:
                if rec.get("priority") == "high":
                    # attach supporting numeric metrics when available
                    supporting_metrics = {}
                    if isinstance(data, dict):
                        metrics = data.get("metrics") or data.get("data") or {}
                        overall = None
                        if isinstance(metrics, dict):
                            overall = metrics.get("overall") or metrics
                        if isinstance(overall, dict):
                            if "avg_roas" in overall:
                                supporting_metrics["avg_roas"] = overall.get("avg_roas")
                            if "avg_ctr" in overall:
                                supporting_metrics["avg_ctr"] = overall.get("avg_ctr")
                    if supporting_metrics:
                        rec["supporting_metrics"] = supporting_metrics

                    # attach a recommended A/B testing plan for high-priority items
                    try:
                        ab_tests = await self._suggest_ab_tests({"current_performance": data.get("metrics", {})})
                        rec["ab_tests"] = ab_tests
                    except Exception:
                        # fail-safe: don't block recommendation generation
                        rec["ab_tests"] = {}
            except Exception:
                # be defensive; skip enrichment on errors
                continue

        result = {
            "recommendations": recommendations,
            "creative_suggestions": creative_suggestions,
            "templates": templates,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in creative library
        self.creative_library[f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = result
        
        return result
    
    async def _generate_performance_recommendations(self, insight: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for performance issues."""
        recommendations = []
        
        category = insight.get("category", "")
        
        if category == "roas":
            recommendations.append({
                "type": "creative_optimization",
                "priority": "high",
                "recommendation": "Optimize ad creatives to improve ROAS",
                "actions": [
                    "Test different creative formats (video vs image)",
                    "A/B test headlines and descriptions",
                    "Optimize for mobile-first design",
                    "Test user-generated content"
                ],
                "expected_impact": "medium",
                "timeline": "1-2 weeks",
                # Added fields for better explainability
                "rationale": insight.get("insight", "ROAS below target"),
                "supporting_insights": [insight.get("category")],
                "confidence": insight.get("confidence", 0.6),
                "expected_uplift": 0.12
            })
        
        elif category == "ctr":
            recommendations.append({
                "type": "engagement_optimization",
                "priority": "high",
                "recommendation": "Improve ad engagement to increase CTR",
                "actions": [
                    "Create more compelling headlines",
                    "Use attention-grabbing visuals",
                    "Test different call-to-action buttons",
                    "Optimize for platform-specific formats"
                ],
                "expected_impact": "high",
                "timeline": "1 week",
                # Explainability fields
                "rationale": insight.get("insight", "CTR below expected"),
                "supporting_insights": [insight.get("category")],
                "confidence": insight.get("confidence", 0.65),
                "expected_uplift": 0.18
            })
        
        return recommendations
    
    async def _generate_trend_recommendations(self, insight: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for negative trends."""
        recommendations = []
        
        category = insight.get("category", "")
        magnitude = insight.get("magnitude", "medium")
        
        if "roas" in category:
            recommendations.append({
                "type": "trend_reversal",
                "priority": "high" if magnitude == "high" else "medium",
                "recommendation": "Reverse declining ROAS trend",
                "actions": [
                    "Refresh ad creatives with new messaging",
                    "Test new audience segments",
                    "Adjust bidding strategies",
                    "Implement dynamic creative optimization"
                ],
                "expected_impact": "high",
                "timeline": "2-3 weeks",
                "rationale": insight.get("insight", "Negative ROAS trend detected"),
                "supporting_insights": [insight.get("category")],
                "confidence": insight.get("confidence", 0.6),
                "expected_uplift": 0.15
            })
        
        return recommendations
    
    async def _generate_campaign_recommendations(self, insight: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for campaign performance."""
        recommendations = []
        
        category = insight.get("category", "")
        
        if category == "performance_gap":
            recommendations.append({
                "type": "campaign_optimization",
                "priority": "medium",
                "recommendation": "Optimize underperforming campaigns",
                "actions": [
                    "Analyze top-performing campaign elements",
                    "Apply successful creative strategies to underperformers",
                    "Test new creative variations",
                    "Optimize audience targeting"
                ],
                "expected_impact": "medium",
                "timeline": "1-2 weeks",
                "rationale": insight.get("insight", "Campaign performance gap"),
                "supporting_insights": [insight.get("category")],
                "confidence": insight.get("confidence", 0.6),
                "expected_uplift": 0.1
            })
        
        return recommendations
    
    async def _generate_audience_recommendations(self, insight: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for audience performance."""
        recommendations = []
        
        category = insight.get("category", "")
        
        if category == "best_audience":
            audience_type = insight.get("audience_type", "")
            recommendations.append({
                "type": "audience_expansion",
                "priority": "high",
                "recommendation": f"Scale {audience_type} audience performance",
                "actions": [
                    f"Create lookalike audiences based on {audience_type}",
                    "Develop audience-specific creative messaging",
                    "Increase budget allocation for high-performing audience",
                    "Test similar audience segments"
                ],
                "expected_impact": "high",
                "timeline": "1 week",
                "rationale": f"{audience_type} shows highest ROAS",
                "supporting_insights": [insight.get("audience_type", audience_type)],
                "confidence": insight.get("confidence", 0.8),
                "expected_uplift": 0.2
            })
        
        return recommendations
    
    async def _generate_platform_recommendations(self, insight: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for platform performance."""
        recommendations = []
        
        category = insight.get("category", "")
        
        if category == "best_platform":
            platform = insight.get("platform", "")
            recommendations.append({
                "type": "platform_optimization",
                "priority": "medium",
                "recommendation": f"Optimize for {platform} platform",
                "actions": [
                    f"Create {platform}-specific creative formats",
                    f"Optimize ad copy for {platform} audience behavior",
                    f"Test {platform}-native features",
                    f"Adjust creative sizing for {platform} specifications"
                ],
                "expected_impact": "medium",
                "timeline": "1 week"
            })
        
        return recommendations
    
    async def _generate_creative_suggestions(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate creative suggestions based on campaign analysis."""
        suggestions = []
        
        campaigns = campaign_data.get("campaigns", [])
        if not campaigns:
            return suggestions
        
        # Analyze top performers
        top_performers = sorted(campaigns, key=lambda x: x["roas"], reverse=True)[:3]
        
        for campaign in top_performers:
            suggestions.append({
                "type": "creative_inspiration",
                "source": f"Top performer: {campaign['campaign_name']}",
                "suggestion": "Analyze and replicate successful creative elements",
                "creative_elements": [
                    "High-performing headline patterns",
                    "Effective visual styles",
                    "Successful call-to-action phrases",
                    "Optimal creative dimensions"
                ],
                "roas": campaign["roas"]
            })
        
        return suggestions
    
    async def _generate_audience_creative_suggestions(self, audience_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate creative suggestions based on audience analysis."""
        suggestions = []
        
        audiences = audience_data.get("audiences", [])
        if not audiences:
            return suggestions
        
        # Generate audience-specific suggestions
        for audience in audiences:
            audience_type = audience["audience_type"]
            suggestions.append({
                "type": "audience_specific_creative",
                "audience": audience_type,
                "suggestion": f"Create {audience_type}-specific creative messaging",
                "messaging_guidelines": [
                    f"Tailor tone and language for {audience_type}",
                    f"Use {audience_type}-relevant imagery",
                    f"Highlight benefits important to {audience_type}",
                    f"Test {audience_type}-specific offers"
                ],
                "roas": audience["roas"]
            })
        
        return suggestions
    
    async def _generate_platform_creative_suggestions(self, platform_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate creative suggestions based on platform analysis."""
        suggestions = []
        
        platforms = platform_data.get("platforms", [])
        if not platforms:
            return suggestions
        
        # Generate platform-specific suggestions
        for platform in platforms:
            platform_name = platform["platform"]
            suggestions.append({
                "type": "platform_specific_creative",
                "platform": platform_name,
                "suggestion": f"Optimize creatives for {platform_name}",
                "creative_guidelines": [
                    f"Use {platform_name}-native ad formats",
                    f"Optimize for {platform_name} user behavior",
                    f"Test {platform_name}-specific features",
                    f"Follow {platform_name} creative best practices"
                ],
                "roas": platform["roas"]
            })
        
        return suggestions
    
    async def _generate_templates(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate creative templates based on data analysis."""
        templates = []
        
        # Generate templates based on performance data
        if "metrics" in data:
            metrics = data["metrics"]
            
            # ROAS-focused template
            if metrics.get("overall", {}).get("avg_roas", 0) < 3.0:
                templates.append({
                    "type": "roas_optimization_template",
                    "name": "ROAS Improvement Template",
                    "description": "Template focused on improving return on ad spend",
                    "elements": [
                        "Value proposition headline",
                        "Social proof elements",
                        "Clear call-to-action",
                        "Benefit-focused copy"
                    ],
                    "format": "image",
                    "priority": "high"
                })
            
            # CTR-focused template
            if metrics.get("overall", {}).get("avg_ctr", 0) < 0.02:
                templates.append({
                    "type": "ctr_optimization_template",
                    "name": "CTR Improvement Template",
                    "description": "Template focused on improving click-through rates",
                    "elements": [
                        "Attention-grabbing headline",
                        "Compelling visual",
                        "Urgency elements",
                        "Engaging call-to-action"
                    ],
                    "format": "video",
                    "priority": "high"
                })
        
        # Generate audience-specific templates
        if "audience_analysis" in data:
            audiences = data["audience_analysis"].get("audiences", [])
            for audience in audiences[:2]:  # Top 2 audiences
                templates.append({
                    "type": "audience_specific_template",
                    "name": f"{audience['audience_type']} Template",
                    "description": f"Template optimized for {audience['audience_type']} audience",
                    "elements": [
                        f"{audience['audience_type']}-focused messaging",
                        "Relevant imagery",
                        "Appropriate tone",
                        "Targeted call-to-action"
                    ],
                    "format": "carousel",
                    "priority": "medium"
                })
        
        return templates
    
    async def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]], creative_suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prioritize recommendations and suggestions."""
        priority = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "immediate_actions": [],
            "long_term_strategies": []
        }

        # Enhanced prioritization using confidence and expected_uplift
        for rec in recommendations:
            rec_priority = rec.get("priority", "medium")
            confidence = float(rec.get("confidence", 0.5) or 0.5)
            expected_uplift = float(rec.get("expected_uplift", 0) or 0)

            # Boost priority if both confidence and expected uplift are high
            if rec_priority == "high" or (confidence >= 0.75 and expected_uplift >= 0.12):
                priority["high_priority"].append(rec)
                priority["immediate_actions"].append(rec)
            elif rec_priority == "medium" or (confidence >= 0.6 and expected_uplift >= 0.05):
                priority["medium_priority"].append(rec)
            else:
                priority["low_priority"].append(rec)

        # Categorize creative suggestions and include high-roas inspirations as immediate
        for suggestion in creative_suggestions:
            if suggestion.get("type") == "creative_inspiration" or suggestion.get("roas", 0) >= 3.0:
                priority["immediate_actions"].append(suggestion)
            else:
                priority["long_term_strategies"].append(suggestion)

        # Sort high priority by a simple score (confidence * expected_uplift)
        def score(item: Dict[str, Any]) -> float:
            return float(item.get("confidence", 0) or 0) * float(item.get("expected_uplift", 0) or 0)

        priority["high_priority"] = sorted(priority["high_priority"], key=score, reverse=True)

        return priority
    
    async def _generate_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific content for ads."""
        content_type = task.get("content_type", "ad_copy")
        target_audience = task.get("target_audience", "general")
        platform = task.get("platform", "facebook")
        requirements = task.get("requirements", {})
        
        content = []
        variations = []
        guidelines = []
        
        # Generate content based on type
        if content_type == "ad_copy":
            content = await self._generate_ad_copy(target_audience, platform, requirements)
        elif content_type == "headlines":
            content = await self._generate_headlines(target_audience, platform, requirements)
        elif content_type == "descriptions":
            content = await self._generate_descriptions(target_audience, platform, requirements)
        
        # Generate variations
        variations = await self._generate_content_variations(content, content_type)
        
        # Generate guidelines
        guidelines = await self._generate_content_guidelines(content_type, target_audience, platform)
        
        return {
            "content": content,
            "variations": variations,
            "guidelines": guidelines,
            "content_type": content_type,
            "target_audience": target_audience,
            "platform": platform
        }
    
    async def _generate_ad_copy(self, target_audience: str, platform: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ad copy content."""
        ad_copies = []
        
        # Generate audience-specific ad copy
        if target_audience.lower() == "broad":
            ad_copies.append({
                "headline": "Comfortable Underwear for Everyone",
                "description": "Experience all-day comfort with our premium collection. Soft, breathable, and designed for your active lifestyle.",
                "call_to_action": "Shop Now",
                "tone": "friendly",
                "length": "medium"
            })
        elif target_audience.lower() == "lookalike":
            ad_copies.append({
                "headline": "Join Thousands of Satisfied Customers",
                "description": "Discover why our customers love our comfortable, high-quality underwear. Limited time offer available.",
                "call_to_action": "Get Yours Today",
                "tone": "persuasive",
                "length": "medium"
            })
        elif target_audience.lower() == "retargeting":
            ad_copies.append({
                "headline": "Don't Miss Out - Complete Your Order",
                "description": "Your cart is waiting! Get the comfort you deserve with our premium underwear collection.",
                "call_to_action": "Complete Purchase",
                "tone": "urgent",
                "length": "short"
            })
        
        return ad_copies
    
    async def _generate_headlines(self, target_audience: str, platform: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate headline content."""
        headlines = []
        
        headline_templates = [
            "Comfortable {product} for {audience}",
            "Premium {product} - Limited Time Offer",
            "Why {audience} Choose Our {product}",
            "All-Day Comfort with {product}",
            "Upgrade Your {product} Collection"
        ]
        
        for template in headline_templates:
            headline = template.format(
                product="underwear",
                audience=target_audience
            )
            headlines.append({
                "text": headline,
                "length": len(headline),
                "tone": "professional",
                "platform": platform
            })
        
        return headlines
    
    async def _generate_descriptions(self, target_audience: str, platform: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate description content."""
        descriptions = []
        
        description_templates = [
            "Experience ultimate comfort with our premium {product} collection. Soft, breathable, and designed for your active lifestyle.",
            "Join thousands of satisfied customers who love our comfortable {product}. Made with quality materials and attention to detail.",
            "Don't compromise on comfort. Our {product} offers the perfect blend of style, comfort, and durability for everyday wear."
        ]
        
        for template in description_templates:
            description = template.format(product="underwear")
            descriptions.append({
                "text": description,
                "length": len(description),
                "tone": "informative",
                "platform": platform
            })
        
        return descriptions
    
    async def _generate_content_variations(self, content: List[Dict[str, Any]], content_type: str) -> List[Dict[str, Any]]:
        """Generate variations of content."""
        variations = []
        
        for item in content:
            # Create variations by modifying tone, length, or style
            if content_type == "ad_copy":
                variation = item.copy()
                variation["tone"] = "casual" if item.get("tone") == "professional" else "professional"
                variations.append(variation)
        
        return variations
    
    async def _generate_content_guidelines(self, content_type: str, target_audience: str, platform: str) -> List[Dict[str, Any]]:
        """Generate content guidelines."""
        guidelines = []
        
        guidelines.append({
            "category": "audience_targeting",
            "guideline": f"Tailor content tone and language for {target_audience} audience",
            "importance": "high"
        })
        
        guidelines.append({
            "category": "platform_optimization",
            "guideline": f"Optimize content format and length for {platform} platform",
            "importance": "high"
        })
        
        guidelines.append({
            "category": "content_quality",
            "guideline": "Ensure content is clear, compelling, and action-oriented",
            "importance": "medium"
        })
        
        return guidelines
    
    async def _suggest_ab_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest A/B testing strategies for creatives."""
        current_performance = task.get("current_performance", {})
        test_objectives = task.get("test_objectives", ["improve_roas", "increase_ctr"])
        budget_constraints = task.get("budget_constraints", {})
        
        test_plans = []
        hypotheses = []
        success_metrics = []
        
        # Generate test plans based on objectives
        for objective in test_objectives:
            if objective == "improve_roas":
                test_plans.append({
                    "test_name": "Creative Format Test",
                    "objective": "Improve ROAS",
                    "test_groups": [
                        {"name": "Control", "description": "Current creative format"},
                        {"name": "Video", "description": "Video creative format"},
                        {"name": "UGC", "description": "User-generated content"}
                    ],
                    "duration": "2 weeks",
                    "budget_allocation": "33% per group"
                })
                
                hypotheses.append({
                    "test": "Creative Format Test",
                    "hypothesis": "Video and UGC formats will outperform current format in ROAS",
                    "rationale": "Video content typically has higher engagement rates"
                })
                
                success_metrics.append({
                    "metric": "ROAS",
                    "target_improvement": "20%",
                    "significance_level": "95%"
                })
            
            elif objective == "increase_ctr":
                test_plans.append({
                    "test_name": "Headline Test",
                    "objective": "Increase CTR",
                    "test_groups": [
                        {"name": "Control", "description": "Current headline"},
                        {"name": "Benefit-focused", "description": "Headline emphasizing benefits"},
                        {"name": "Urgency", "description": "Headline with urgency elements"}
                    ],
                    "duration": "1 week",
                    "budget_allocation": "33% per group"
                })
                
                hypotheses.append({
                    "test": "Headline Test",
                    "hypothesis": "Benefit-focused and urgency headlines will increase CTR",
                    "rationale": "Clear benefits and urgency drive immediate action"
                })
                
                success_metrics.append({
                    "metric": "CTR",
                    "target_improvement": "15%",
                    "significance_level": "95%"
                })
        
        return {
            "test_plans": test_plans,
            "hypotheses": hypotheses,
            "success_metrics": success_metrics,
            "budget_constraints": budget_constraints,
            "recommended_tests": test_plans[:2]  # Top 2 recommended tests
        }
