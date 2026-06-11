"""NOVA AI Main Entry Point"""

import logging
import asyncio
from src.config import settings
from src.core.agent.coordinator import CoordinatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("NOVA AI - Personal Windows Agent OS")
    logger.info("Version: 0.1.0 (Prototype)")
    logger.info("=" * 60)
    
    try:
        # Initialize coordinator agent
        coordinator = CoordinatorAgent()
        await coordinator.initialize()
        
        logger.info("NOVA AI initialized successfully")
        logger.info("Ready for commands...")
        
        # Start interactive loop
        await coordinator.run()
        
    except Exception as e:
        logger.error(f"Error initializing NOVA AI: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
