# CredentialWatch: Alert MCP Server

## Overview

CredentialWatch is a demo product for the **Hugging Face "MCP 1st Birthday / Gradio Agents Hackathon"**. It is designed to act as a unified, queryable view of provider credentials and a proactive alerting system for expirations (state licenses, board certs, DEA/CDS, etc.) in a US-style healthcare setting.

The system leverages:
-   **Model Context Protocol (MCP)** for standardized tool interfaces.
-   **LangGraph** for agentic workflows (sweeps, Q&A).
-   **Gradio** for the user interface.
-   **FastAPI & SQLite** for backend services and data persistence.

### System Architecture

The complete CredentialWatch system consists of three separate MCP servers:
1.  **npi_mcp**: Read-only access to the public NPPES NPI Registry.
2.  **cred_db_mcp**: Internal provider & credential database operations.
3.  **alert_mcp** (This Repository): Alert logging, listing, and resolution.

These servers interact with a **LangGraph Agent** and **Gradio UI** to provide a seamless experience for managing provider credentials and risks.

---

## This Repository: `alert_mcp` & `alert_mcp_server`

This repository specifically houses the **Alert MCP** component, which includes:

1.  **`src/alert_mcp`**: A FastAPI backend service that manages the `alerts` table in a SQLite database. It provides endpoints to log alerts, retrieve open alerts, and mark them as resolved.
2.  **`src/alert_mcp_server`**: A Gradio-based MCP server. It acts as a frontend/wrapper that exposes the alert capabilities as MCP tools (via SSE) and provides a simple web UI for testing and interaction.

### Features
-   **Log Alert**: Create new alerts with severity levels (info, warning, critical).
-   **View Alerts**: Query open alerts, filtered by provider or severity.
-   **Resolve Alert**: Mark alerts as resolved with a note.
-   **Summarize**: Get a breakdown of alerts by severity.
-   **MCP Support**: Exposes these functions as MCP tools for agents to use.

---

## Prerequisites

-   **Python 3.11**
-   **uv** (recommended for dependency management)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd <repo-dir>
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```
    Or using pip:
    ```bash
    pip install .
    ```

## Configuration

The system uses environment variables for configuration. Create a `.env` file or set them in your environment:

```bash
# src/alert_mcp_server/config.py
ALERT_API_BASE_URL=http://localhost:8000  # URL of the backend alert_mcp service
DB_FILE_PATH=/data/credentialwatch.db     # Path to SQLite DB (used by backend)
```

## Usage

### 1. Run the Backend (`alert_mcp`)

The backend service manages the database and API.

```bash
uv run uvicorn src.alert_mcp.main:app --reload --port 8000
```
This will start the FastAPI server at `http://localhost:8000`. It will automatically create the SQLite database at `DB_FILE_PATH` (defaulting to `./credentialwatch.db` or similar if not set).

### 2. Run the Gradio MCP Server (`alert_mcp_server`)

The Gradio server connects to the backend and exposes the UI and MCP tools.

```bash
uv run python -m src.alert_mcp_server.main
```
This will launch the Gradio interface (usually at `http://localhost:7860`).

### Using with an MCP Client

The `alert_mcp_server` exposes MCP tools via SSE (Server-Sent Events). An MCP-compatible agent (like the CredentialWatch LangGraph agent) can connect to this server to:
-   `log_alert(...)`
-   `get_open_alerts(...)`
-   `mark_alert_resolved(...)`

## Testing

Run the test suite using `pytest`:

```bash
uv run pytest
```

## Project Structure

```
.
├── src/
│   ├── alert_mcp/          # FastAPI Backend & DB Models
│   │   ├── main.py         # App entrypoint
│   │   ├── models.py       # SQLAlchemy models (Alert)
│   │   ├── db.py           # DB connection logic
│   │   └── ...
│   └── alert_mcp_server/   # Gradio UI & MCP Tool Wrapper
│       ├── main.py         # Gradio app entrypoint
│       ├── tools.py        # Client logic to talk to backend
│       └── ...
├── tests/                  # Test suite
└── pyproject.toml          # Dependencies
```

## License

MIT
