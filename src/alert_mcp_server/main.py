import gradio as gr
from .tools import log_alert, get_open_alerts, mark_alert_resolved, summarize_alerts

# Define the Gradio interface
# We can use a TabbedInterface to organize the tools for the UI,
# which also registers them as MCP tools.

def create_demo():
    with gr.Blocks(title="CredentialWatch Alert MCP") as demo:
        gr.Markdown("# CredentialWatch Alert MCP Server")
        gr.Markdown("This server exposes tools for managing alerts via MCP. It also provides a simple UI.")

        with gr.Tab("Log Alert"):
            gr.Markdown("## Log a new alert")
            with gr.Row():
                t1_provider_id = gr.Number(label="Provider ID", value=1, precision=0)
                t1_credential_id = gr.Number(label="Credential ID (Optional)", value=None, precision=0)

            with gr.Row():
                t1_severity = gr.Dropdown(choices=["info", "warning", "critical"], label="Severity", value="info")
                t1_window_days = gr.Number(label="Window Days", value=30, precision=0)

            t1_message = gr.Textbox(label="Message")
            t1_channel = gr.Textbox(label="Channel", value="ui")

            t1_output = gr.JSON(label="Response")
            t1_btn = gr.Button("Log Alert")

            t1_btn.click(
                fn=log_alert,
                inputs=[t1_provider_id, t1_severity, t1_window_days, t1_message, t1_credential_id, t1_channel],
                outputs=t1_output
            )

        with gr.Tab("Get Open Alerts"):
            gr.Markdown("## List open alerts")
            t2_provider_id = gr.Number(label="Provider ID (Optional)", value=None, precision=0)
            t2_severity = gr.Dropdown(choices=["info", "warning", "critical", None], label="Severity (Optional)", value=None)

            t2_output = gr.JSON(label="Open Alerts")
            t2_btn = gr.Button("Get Alerts")

            t2_btn.click(
                fn=get_open_alerts,
                inputs=[t2_provider_id, t2_severity],
                outputs=t2_output
            )

        with gr.Tab("Resolve Alert"):
            gr.Markdown("## Mark alert as resolved")
            t3_alert_id = gr.Number(label="Alert ID", precision=0)
            t3_note = gr.Textbox(label="Resolution Note")

            t3_output = gr.JSON(label="Updated Alert")
            t3_btn = gr.Button("Resolve")

            t3_btn.click(
                fn=mark_alert_resolved,
                inputs=[t3_alert_id, t3_note],
                outputs=t3_output
            )

        with gr.Tab("Summarize Alerts"):
            gr.Markdown("## Summary of alerts")
            t4_window = gr.Number(label="Window Days (Optional)", value=None, precision=0)

            t4_output = gr.JSON(label="Summary")
            t4_btn = gr.Button("Summarize")

            t4_btn.click(
                fn=summarize_alerts,
                inputs=[t4_window],
                outputs=t4_output
            )

    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(mcp_server=True)
