"""
Main entry point for the Agentic Facebook Performance Analyst system.
"""
import json
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import config
from src.core.agent_base import AgentRegistry, AgentMessage, MessageType
from src.core.memory_systems import AdaptiveMemoryManager
from src.utils.data_processor import FacebookAdsDataProcessor
from src.utils.report_generator import ReportGenerator
from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_generator import CreativeGeneratorAgent

# Configure logging
# Ensure the logs directory exists before configuring file handlers so
# logging.FileHandler doesn't fail in CI or fresh checkouts.
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, config.get_logging_config().get('level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AgenticFacebookAnalyst:
    """Main orchestrator for the agentic Facebook performance analysis system."""
    
    def __init__(self):
        """Initialize the system."""
        self.registry = AgentRegistry()
        self.data_processor: Optional[FacebookAdsDataProcessor] = None
        self.memory_manager: Optional[AdaptiveMemoryManager] = None
        self.report_generator: Optional[ReportGenerator] = None
        self.agents_initialized = False
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Initialize components
        self._initialize_memory_manager()
        self._initialize_data_processor()
        self._initialize_report_generator()
        self._initialize_agents()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = ['logs', 'reports', 'data/memory']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _initialize_memory_manager(self) -> None:
        """Initialize memory manager."""
        try:
            memory_config = config.get_memory_config()
            self.memory_manager = AdaptiveMemoryManager(memory_config)
            logger.info("Memory manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            sys.exit(1)
    
    def _initialize_report_generator(self) -> None:
        """Initialize report generator."""
        try:
            reports_config = config.get_reports_config()
            output_dir = reports_config.get("output_dir", "reports")
            self.report_generator = ReportGenerator(output_dir)
            logger.info("Report generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize report generator: {e}")
            sys.exit(1)
    
    def _initialize_data_processor(self) -> None:
        """Initialize data processor."""
        try:
            csv_path = config.data_csv_path
            if not Path(csv_path).exists():
                logger.error(f"Data file not found: {csv_path}")
                sys.exit(1)
            
            self.data_processor = FacebookAdsDataProcessor(csv_path)
            logger.info("Data processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize data processor: {e}")
            sys.exit(1)
    
    def _initialize_agents(self) -> None:
        """Initialize all agents."""
        try:
            # Initialize agents with their configurations
            planner_config = config.get_agent_config('planner')
            data_agent_config = config.get_agent_config('data_agent')
            insight_agent_config = config.get_agent_config('insight_agent')
            evaluator_config = config.get_agent_config('evaluator')
            creative_generator_config = config.get_agent_config('creative_generator')
            
            # Create agents
            planner = PlannerAgent("planner_001", "Planner", planner_config)
            data_agent = DataAgent("data_001", "DataAgent", data_agent_config)
            insight_agent = InsightAgent("insight_001", "InsightAgent", insight_agent_config)
            evaluator = EvaluatorAgent("evaluator_001", "Evaluator", evaluator_config)
            creative_generator = CreativeGeneratorAgent("creative_001", "CreativeGenerator", creative_generator_config)
            
            # Set data processor for data agent
            data_agent.set_data_processor(self.data_processor)
            
            # Register agents
            self.registry.register_agent(planner)
            self.registry.register_agent(data_agent)
            self.registry.register_agent(insight_agent)
            self.registry.register_agent(evaluator)
            self.registry.register_agent(creative_generator)
            
            self.agents_initialized = True
            logger.info("All agents initialized and registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            sys.exit(1)
    
    async def analyze_performance(self, query: str) -> Dict[str, Any]:
        """Main analysis method."""
        logger.info(f"Starting analysis for query: {query}")
        
        try:
            # Create initial message for planner
            initial_message = AgentMessage(
                message_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sender="system",
                recipient="planner_001",
                message_type=MessageType.REQUEST,
                content={
                    "query": query,
                    "data_summary": self.data_processor.get_data_summary(),
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now()
            )
            
            # Start the analysis workflow
            result = await self.registry.route_message(initial_message)
            
            if result:
                logger.info("Analysis completed successfully")

                # Only generate reports if the planner returned a mapping-like result
                if self.report_generator:
                    if isinstance(result.content, dict):
                        report_files = self.report_generator.generate_report(result.content, query)
                        logger.info(f"Reports generated: {report_files}")
                    else:
                        logger.error("Analysis returned non-dict result.content; skipping report generation")

                # Store results in memory (only store dicts)
                if self.memory_manager and isinstance(result.content, dict):
                    await self.memory_manager.store(f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}", result.content, "long_term")

                return result.content
            else:
                logger.error("Analysis failed - no result from planner")
                return {"error": "Analysis failed"}
                
        except Exception as e:
            # Log full exception stack to help trace where the failure occurred
            logger.exception(f"Analysis failed with error: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        status = {
            "system": "Agentic Facebook Performance Analyst",
            "version": "1.0.0",
            "agents": [],
            "data_processor": {
                "initialized": self.data_processor is not None,
                "records": len(self.data_processor.df) if self.data_processor else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Get status from all agents
        for agent in self.registry.get_all_agents():
            try:
                agent_status = await agent.health_check()
                status["agents"].append(agent_status)
            except Exception as e:
                logger.error(f"Failed to get status from {agent}: {e}")
        
        return status
    
    async def shutdown(self) -> None:
        """Shutdown the system gracefully."""
        logger.info("Shutting down system...")
        
        # Clear agent memories
        for agent in self.registry.get_all_agents():
            agent.clear_memory()
        
        # Clear memory manager
        if self.memory_manager:
            await self.memory_manager.clear("short_term")
        
        logger.info("System shutdown complete")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python src/run.py \"<analysis query>\"")
        print("Example: python src/run.py \"Analyze ROAS drop in last 7 days\"")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Initialize system
    analyst = AgenticFacebookAnalyst()
    
    try:
        # Perform analysis
        result = await analyst.analyze_performance(query)
        
        # Print results
        print("\n" + "="*50)
        print("ANALYSIS RESULTS")
        print("="*50)
        print(f"Query: {query}")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Get system status
        status = await analyst.get_system_status()
        print(f"\nSystem Status: {json.dumps(status, indent=2)}")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)
    finally:
        await analyst.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
