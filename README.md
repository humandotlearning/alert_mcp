---
title: CredentialWatch Alert MCP
emoji: 🩺
colorFrom: blue
colorTo: purple
sdk: gradio
python_version: 3.11
sdk_version: 6.0.0
app_file: app.py
fullWidth: true
short_description: "Gradio MCP server for healthcare credential alerts."
tags:
  - mcp
  - gradio
  - tools
  - healthcare
pinned: false
---

# CredentialWatch Alert MCP Server

Agent-ready Gradio Space that exposes healthcare credential alerts tools (log, view, resolve) over **Model Context Protocol (MCP)**.

## Hugging Face Space

This repository is designed to run as a **Gradio Space**.

- SDK: Gradio (`sdk: gradio` in the README header)
- Entry file: `app.py` (set via `app_file` in the YAML header)
- Python: 3.11 (pinned with `python_version`)

When you push this repo to a Space with SDK = **Gradio**, the UI and the MCP server will be started automatically.

## MCP Server

This Space exposes its tools via **Model Context Protocol (MCP)** using Gradio.

### How MCP is enabled

In `app.py` we:

- initialize the database
- launch the app with MCP support: `demo.launch(mcp_server=True)`

### MCP endpoints

When the Space is running, Gradio exposes:

- **MCP SSE endpoint**: `https://<space-host>/gradio_api/mcp/sse`
- **MCP schema**: `https://<space-host>/gradio_api/mcp/schema`

## Using this Space from an MCP client

### Easiest: Hugging Face MCP Server (no manual config)

1. Go to your HF **MCP settings**: https://huggingface.co/settings/mcp
2. Add this Space under **Spaces Tools** (look for the MCP badge on the Space).
3. Restart your MCP client (VS Code, Cursor, Claude Code, etc.).
4. The tools from this Space will appear as MCP tools and can be called directly.

### Manual config (generic MCP client using mcp-remote)

If your MCP client uses a JSON config, you can point it to the SSE endpoint via `mcp-remote`:

```jsonc
{
  "mcpServers": {
    "credentialwatch-alert": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://<space-host>/gradio_api/mcp/sse"
      ]
    }
  }
}
```

Replace `<space-host>` with the full URL of your Space.

## Local development

```bash
# 1. Install deps
uv pip install -r requirements.txt

# 2. Run locally
uv run python app.py
```

The local server will be available at http://127.0.0.1:7860, and MCP at http://127.0.0.1:7860/gradio_api/mcp/sse.

## Deploying to Hugging Face Spaces

1. Create a new Space with SDK = **Gradio**.
2. Push this repo to the Space (Git or `huggingface_hub`).
3. Ensure the YAML header in `README.md` is present and correct.
4. Wait for the Space to build and start — it should show an **MCP badge** automatically.

## Troubleshooting

- If the Space shows **Configuration error**, verify `sdk`, `app_file`, and `python_version` in the YAML header.
- If the **MCP badge** doesn't appear, confirm `demo.launch(mcp_server=True)` is called in `app.py`.
- Ensure `README.md` is at the root and not tracked by LFS.

---

## Original Documentation

### Overview

CredentialWatch is a demo product for the **Hugging Face "MCP 1st Birthday / Gradio Agents Hackathon"**. It is designed to act as a unified, queryable view of provider credentials and a proactive alerting system.

### Features
-   **Log Alert**: Create new alerts with severity levels (info, warning, critical).
-   **View Alerts**: Query open alerts, filtered by provider or severity.
-   **Resolve Alert**: Mark alerts as resolved with a note.
-   **Summarize**: Get a breakdown of alerts by severity.
-   **MCP Support**: Exposes these functions as MCP tools for agents to use.

### Project Structure

```
.
├── app.py                  # Entry point for HF Spaces
├── requirements.txt        # Dependencies
├── src/
│   ├── alert_mcp/          # Backend logic & DB Models
│   └── alert_mcp_server/   # Gradio UI & Tool Wrappers
└── ...
```
