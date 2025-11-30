import os
import sys
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Windows-specific event loop policy to prevent "Event loop is closed" errors
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.alert_mcp.db import init_db
from src.alert_mcp_server.app import create_demo

def main():
    try:
        # Initialize the database
        logger.info("Initializing database...")
        init_db()

        # Create and launch the demo
        logger.info("Creating Gradio app...")
        demo = create_demo()

        logger.info("Launching server...")
        demo.launch(mcp_server=True)
    except Exception as e:
        logger.error(f"Failed to launch app: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
