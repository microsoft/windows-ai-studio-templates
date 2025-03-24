import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import gradio as gr

from mcp_chat import MCPChat

client = MCPChat()

async def ask(text: str):
    output = ""
    async for delta in client.chatWithTools(text):
        yield delta
        output += delta

def configure_gradio(app: FastAPI):
    # Gradio UI setup
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=4):
                user_text = gr.Textbox(placeholder="Input", label="User input")
                # model_output = gr.Textbox(label="Output", lines=10, interactive=False)
                model_output = gr.Markdown(label="Output", height=400, container=True, show_label=True)
                button_submit = gr.Button(value="Submit")

        params = [user_text]
        user_text.submit(ask, params, model_output)
        button_submit.click(ask, params, model_output)

        return gr.mount_gradio_app(app, demo, path="/chat")

app = FastAPI()
app = configure_gradio(app)
app.mount("/working", StaticFiles(directory=".working"), name="working")
@app.get("/")
def root():
    return "Chat on /chat and static files on /working"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
