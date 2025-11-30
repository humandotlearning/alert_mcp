import os
import sys

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.alert_mcp.db import init_db
from src.alert_mcp_server.app import create_demo

# Initialize the database
init_db()

# Create and launch the demo
demo = create_demo()

if __name__ == "__main__":
    demo.launch(mcp_server=True)
