"""
Planner Agent - Orchestrates the analysis workflow and coordinates other agents.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.core.agent_base import BaseAgent, AgentCapability, AgentMessage, MessageType, AgentStatus

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Planner agent that orchestrates the analysis workflow."""
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        """Initialize planner agent."""
        super().__init__(agent_id, name, config)
        self.workflow_steps: List[Dict[str, Any]] = []
        self.current_step = 0
        self.analysis_context: Dict[str, Any] = {}
    
    def _initialize_capabilities(self) -> None:
        """Initialize planner capabilities."""
        self.capabilities = [
            AgentCapability(
                name="workflow_planning",
                description="Plan and orchestrate analysis workflows",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "data_summary": {"type": "object"},
                        "constraints": {"type": "object"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "workflow": {"type": "array"},
                        "estimated_duration": {"type": "number"},
                        "required_agents": {"type": "array"}
                    }
                },
                required_params=["query"]
            ),
            AgentCapability(
                name="task_decomposition",
                description="Break down complex analysis tasks into smaller subtasks",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["task"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "subtasks": {"type": "array"},
                        "dependencies": {"type": "array"},
                        "priority": {"type": "array"}
                    }
                },
                required_params=["task"]
            ),
            AgentCapability(
                name="agent_coordination",
                description="Coordinate multiple agents to complete analysis tasks",
                input_schema={
                    "type": "object",
                    "properties": {
                        "agents": {"type": "array"},
                        "tasks": {"type": "array"},
                        "context": {"type": "object"}
                    },
                    "required": ["agents", "tasks"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "coordination_plan": {"type": "object"},
                        "handoff_points": {"type": "array"},
                        "expected_outcomes": {"type": "array"}
                    }
                },
                required_params=["agents", "tasks"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message."""
        try:
            self.update_status(AgentStatus.BUSY)
            
            if message.message_type == MessageType.REQUEST:
                if "query" in message.content:
                    # This is an analysis request
                    result = await self.execute_analysis_workflow(message.content)
                else:
                    # Handle other request types
                    result = await self.execute_task(message.content)
            else:
                # Handle other message types
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
        task_type = task.get("task_type", "unknown")
        
        if task_type == "workflow_planning":
            return await self._plan_workflow(task)
        elif task_type == "task_decomposition":
            return await self._decompose_task(task)
        elif task_type == "agent_coordination":
            return await self._coordinate_agents(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def execute_analysis_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the main analysis workflow."""
        query = request.get("query", "")
        data_summary = request.get("data_summary", {})
        
        logger.info(f"Starting analysis workflow for query: {query}")
        
        # Store analysis context
        self.analysis_context = {
            "query": query,
            "data_summary": data_summary,
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "results": {}
        }
        
        # Plan the workflow
        workflow_plan = await self._plan_analysis_workflow(query, data_summary)
        
        # Execute the workflow steps
        results = await self._execute_workflow_steps(workflow_plan)
        
        # Compile final results
        final_result = {
            "query": query,
            "workflow": workflow_plan,
            "results": results,
            "summary": await self._generate_analysis_summary(results),
            "timestamp": datetime.now().isoformat(),
            "duration": self._calculate_duration()
        }
        
        # Store results in memory
        self.store_memory("last_analysis", final_result)
        
        return final_result
    
    async def _plan_analysis_workflow(self, query: str, data_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan the analysis workflow based on the query."""
        workflow = []
        
        # Analyze query to determine required steps
        query_lower = query.lower()
        
        # Data analysis step
        if any(keyword in query_lower for keyword in ["analyze", "performance", "metrics", "roas", "ctr", "spend"]):
            workflow.append({
                "step": "data_analysis",
                "agent": "data_agent",
                "description": "Analyze performance metrics and trends",
                "inputs": {"query": query, "data_summary": data_summary},
                "expected_outputs": ["metrics_analysis", "trends", "anomalies"]
            })

        # Ensure we always run insight generation after data analysis so reports contain
        # synthesized insights even when the user's query doesn't explicitly request them.
        steps = [s["step"] for s in workflow]
        if "data_analysis" in steps and "insight_generation" not in steps:
            workflow.append({
                "step": "insight_generation",
                "agent": "insight_agent",
                "description": "Generate insights and identify patterns",
                "inputs": {"query": query},
                "expected_outputs": ["insights", "patterns", "correlations"]
            })
            # Also ensure creative recommendations are generated so reports have
            # actionable recommendations by default.
            if "creative_recommendations" not in steps:
                workflow.append({
                    "step": "creative_recommendations",
                    "agent": "creative_generator",
                    "description": "Generate creative recommendations",
                    "inputs": {"query": query},
                    "expected_outputs": ["recommendations", "creative_suggestions"]
                })
        
        # Insight generation step (retained for explicit keyword matching — the
        # planner already ensured insight_generation runs when data_analysis is present)
        if any(keyword in query_lower for keyword in ["insight", "pattern", "correlation", "why", "reason"]):
            # avoid duplicate step if already added
            if not any(s["step"] == "insight_generation" for s in workflow):
                workflow.append({
                    "step": "insight_generation",
                    "agent": "insight_agent",
                    "description": "Generate insights and identify patterns",
                    "inputs": {"query": query},
                    "expected_outputs": ["insights", "patterns", "correlations"]
                })
        
        # Evaluation step
        workflow.append({
            "step": "evaluation",
            "agent": "evaluator",
            "description": "Evaluate findings and validate insights",
            "inputs": {"query": query},
            "expected_outputs": ["evaluation", "confidence_scores", "validation"]
        })
        
        # Creative recommendations step
        if any(keyword in query_lower for keyword in ["recommend", "suggest", "improve", "optimize", "creative"]):
            workflow.append({
                "step": "creative_recommendations",
                "agent": "creative_generator",
                "description": "Generate creative recommendations",
                "inputs": {"query": query},
                "expected_outputs": ["recommendations", "creative_suggestions"]
            })
        
        return workflow
    
    async def _execute_workflow_steps(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the workflow steps."""
        results = {}
        
        for i, step in enumerate(workflow):
            logger.info(f"Executing step {i+1}/{len(workflow)}: {step['step']}")
            
            try:
                # Create message for the target agent
                step_message = AgentMessage(
                    message_id=f"step_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    sender=self.agent_id,
                    recipient=step["agent"],
                    message_type=MessageType.REQUEST,
                    content={
                        "task_type": step["step"],
                        "inputs": step["inputs"],
                        "workflow_context": self.analysis_context
                    },
                    timestamp=datetime.now()
                )
                
                # Execute step (in a real implementation, this would route to the actual agent)
                # Pass the results accumulated so far to the simulator so later steps can use earlier outputs
                step_result = await self._simulate_agent_execution(step, results)
                
                results[step["step"]] = step_result
                self.analysis_context["steps_completed"].append(step["step"])
                
                logger.info(f"Step {step['step']} completed successfully")
                
            except Exception as e:
                logger.error(f"Error executing step {step['step']}: {e}")
                results[step["step"]] = {"error": str(e)}
        
        return results
    
    async def _simulate_agent_execution(self, step: Dict[str, Any], results_so_far: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent execution (placeholder for actual agent communication)."""
        # This is a placeholder - in the real implementation, this would communicate with actual agents
        await asyncio.sleep(0.1)  # Simulate processing time
        
        step_name = step["step"]
        
        if step_name == "data_analysis":
            return {
                "metrics": {
                    "avg_roas": 3.2,
                    "total_spend": 15000,
                    "total_revenue": 48000,
                    "avg_ctr": 0.018
                },
                "trends": {
                    "roas_trend": -0.15,
                    "spend_trend": 0.05,
                    "revenue_trend": -0.08
                },
                "anomalies": [
                    {"date": "2025-01-13", "metric": "roas", "value": 0.0, "z_score": 3.2}
                ]
            }
        elif step_name == "insight_generation":
            return {
                "insights": [
                    "ROAS has been declining over the past week",
                    "Video creatives perform better than image creatives",
                    "Lookalike audiences show higher conversion rates"
                ],
                "patterns": [
                    {"pattern": "weekend_performance", "description": "Lower performance on weekends"},
                    {"pattern": "creative_type_correlation", "description": "Video > UGC > Image > Carousel"}
                ]
            }
        elif step_name == "evaluation":
            return {
                "confidence_scores": {
                    "roas_decline": 0.85,
                    "creative_performance": 0.92,
                    "audience_insights": 0.78
                },
                "validation": {
                    "statistical_significance": True,
                    "sample_size": "adequate",
                    "data_quality": "high"
                }
            }
        elif step_name == "creative_recommendations":
            # Build structured recommendations using previous results when available
            insights = results_so_far.get("insight_generation", {}).get("insights", [])
            data_analysis = results_so_far.get("data_analysis", {})

            recommendations = []
            creative_suggestions = []

            # Simple mapping heuristics from insights to structured recommendations
            for insight in insights:
                text = str(insight).lower()
                if "roas" in text or "declin" in text:
                    recommendations.append({
                        "type": "creative_optimization",
                        "priority": "high",
                        "recommendation": "Optimize ad creatives to address ROAS decline",
                        "actions": [
                            "Increase share of video creatives",
                            "A/B test headlines and offers",
                            "Pause underperforming creatives"
                        ],
                        "expected_impact": "high",
                        "timeline": "1-2 weeks",
                        "rationale": insight,
                        "supporting_insights": ["roas"],
                        "confidence": results_so_far.get("evaluation", {}).get("confidence_scores", {}).get("roas_decline", 0.6),
                        "expected_uplift": 0.12,
                        "supporting_metrics": {
                            "avg_roas": data_analysis.get("metrics", {}).get("avg_roas")
                        },
                        "ab_tests": {
                            "test_name": "Video vs Image",
                            "objective": "Improve ROAS",
                            "duration": "2 weeks"
                        }
                    })
                elif "video" in text:
                    recommendations.append({
                        "type": "creative_investment",
                        "priority": "medium",
                        "recommendation": "Increase investment in video creative formats",
                        "actions": ["Allocate more budget to video", "Produce 2-3 new video concepts"],
                        "expected_impact": "medium",
                        "timeline": "1 week",
                        "rationale": insight,
                        "supporting_insights": ["creative_type"],
                        "confidence": 0.7,
                        "expected_uplift": 0.08,
                        "supporting_metrics": {
                            "video_share": data_analysis.get("metrics", {}).get("video_share")
                        }
                    })
                else:
                    # Generic recommendation
                    recommendations.append({
                        "type": "general",
                        "priority": "low",
                        "recommendation": str(insight),
                        "actions": [],
                        "expected_impact": "low",
                        "timeline": "",
                        "rationale": insight,
                        "supporting_insights": [],
                        "confidence": 0.5,
                        "expected_uplift": 0.02
                    })

            # Creative suggestions inferred from data
            if data_analysis:
                # Suggest video content if video outperforms
                creative_suggestions.append({
                    "type": "creative_inspiration",
                    "source": "Top performers",
                    "suggestion": "Create lifestyle video content",
                    "creative_elements": ["Story-driven visuals", "Short hook", "Strong CTA"],
                    "roas": data_analysis.get("metrics", {}).get("avg_roas")
                })

            return {"recommendations": recommendations, "creative_suggestions": creative_suggestions}
        else:
            return {"status": "completed", "step": step_name}
    
    async def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        summary = {
            "key_findings": [],
            "recommendations": [],
            "confidence_level": "medium",
            "next_steps": []
        }
        
        # Extract key findings from results
        if "insight_generation" in results:
            insights = results["insight_generation"].get("insights", [])
            summary["key_findings"].extend(insights[:3])  # Top 3 insights
        
        # Extract recommendations
        if "creative_recommendations" in results:
            recommendations = results["creative_recommendations"].get("recommendations", [])
            summary["recommendations"].extend(recommendations[:3])  # Top 3 recommendations

        # If no recommendations were generated by agents, synthesize heuristics
        if not summary["recommendations"]:
            synthesized = self._synthesize_recommendations(results)
            if synthesized:
                summary["recommendations"].extend(synthesized[:3])
        
        # Determine confidence level
        if "evaluation" in results:
            confidence_scores = results["evaluation"].get("confidence_scores", {})
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5
            
            if avg_confidence > 0.8:
                summary["confidence_level"] = "high"
            elif avg_confidence > 0.6:
                summary["confidence_level"] = "medium"
            else:
                summary["confidence_level"] = "low"
        
        return summary

    def _synthesize_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Create heuristic recommendations from data_analysis, trends, and anomalies.

        This provides a safe fallback so reports contain actionable guidance even if
        the creative generator wasn't invoked or returned nothing.
        """
        recs: List[str] = []

        # Heuristic from metrics
        data_analysis = results.get("data_analysis", {})
        metrics = data_analysis.get("metrics", {})
        avg_roas = metrics.get("avg_roas") if isinstance(metrics, dict) else None
        avg_ctr = metrics.get("avg_ctr") if isinstance(metrics, dict) else None

        try:
            if isinstance(avg_roas, (int, float)):
                if avg_roas < 2.0:
                    recs.append("Investigate low ROAS: prioritize high-ROAS campaigns and reallocate budget to top-performing creative types (e.g., video/UGC).")
                elif avg_roas < 3.0:
                    recs.append("Run A/B tests on creatives for underperforming campaigns and consider reallocating budget to better-performing segments.")

            if isinstance(avg_ctr, (int, float)):
                if avg_ctr < 0.01:
                    recs.append("Improve ad creative and CTAs to lift CTR: test stronger calls-to-action and creative variants.")

        except Exception:
            # Be defensive — don't raise from heuristic generation
            pass

        # Trend-based heuristics
        trends = data_analysis.get("trends", {}) if isinstance(data_analysis, dict) else {}
        if isinstance(trends, dict):
            # Look for ROAS trend indicators (keys might be metric_trend or numeric scalars)
            roas_trend = None
            # trends could be a mapping of metric->{change_percent} or metric->float
            if "roas_trend" in trends:
                val = trends.get("roas_trend")
                if isinstance(val, dict):
                    roas_trend = val.get("change_percent")
                elif isinstance(val, (int, float)):
                    roas_trend = val

            if isinstance(roas_trend, (int, float)) and roas_trend < 0:
                recs.append("ROAS is trending down — investigate recent creative changes and audience shifts; prioritize tests on top-performing creatives.")

        # Anomalies
        anomalies = data_analysis.get("anomalies", []) if isinstance(data_analysis, dict) else []
        if anomalies:
            # Collect dates if available
            dates = [a.get("date") for a in anomalies if isinstance(a, dict) and a.get("date")]
            if dates:
                recs.append(f"Investigate anomalies around dates: {', '.join(dates)}; consider pausing affected campaigns until root cause is found.")
            else:
                recs.append("Investigate detected anomalies in performance data and validate data integrity.")

        return recs
    
    def _calculate_duration(self) -> str:
        """Calculate analysis duration."""
        if "start_time" in self.analysis_context:
            start_time = datetime.fromisoformat(self.analysis_context["start_time"])
            duration = datetime.now() - start_time
            return f"{duration.total_seconds():.2f} seconds"
        return "unknown"
    
    async def _plan_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a workflow for the given task."""
        return {
            "workflow": [
                {"step": "data_collection", "agent": "data_agent"},
                {"step": "analysis", "agent": "insight_agent"},
                {"step": "validation", "agent": "evaluator"}
            ],
            "estimated_duration": "5-10 minutes",
            "required_agents": ["data_agent", "insight_agent", "evaluator"]
        }
    
    async def _decompose_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose a complex task into subtasks."""
        return {
            "subtasks": [
                {"id": "subtask_1", "description": "Data collection and validation"},
                {"id": "subtask_2", "description": "Statistical analysis"},
                {"id": "subtask_3", "description": "Pattern recognition"},
                {"id": "subtask_4", "description": "Insight generation"}
            ],
            "dependencies": [
                {"from": "subtask_1", "to": "subtask_2"},
                {"from": "subtask_2", "to": "subtask_3"},
                {"from": "subtask_3", "to": "subtask_4"}
            ],
            "priority": ["subtask_1", "subtask_2", "subtask_3", "subtask_4"]
        }
    
    async def _coordinate_agents(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for task execution."""
        return {
            "coordination_plan": {
                "phase_1": {"agents": ["data_agent"], "duration": "2 minutes"},
                "phase_2": {"agents": ["insight_agent"], "duration": "3 minutes"},
                "phase_3": {"agents": ["evaluator"], "duration": "1 minute"}
            },
            "handoff_points": [
                {"from": "data_agent", "to": "insight_agent", "data": "processed_data"},
                {"from": "insight_agent", "to": "evaluator", "data": "insights"}
            ],
            "expected_outcomes": [
                "Data analysis report",
                "Insight summary",
                "Validation results"
            ]
        }
