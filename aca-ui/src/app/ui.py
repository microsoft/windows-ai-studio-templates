import asyncio
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import gradio as gr

from access import get_access_token

target_url = "https://some.url"

def ask(text: str):
    session = requests.Session()
    response = session.get(
        f"{target_url}/chat",
        headers={
            "authorization": f"{get_access_token(target_url)}",
        },
        params={"text": text},
        stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            output += line.decode("utf-8") + "\n\n"
            yield output

def configure_gradio(app: FastAPI):
    # Gradio UI setup
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=4):
                user_text = gr.Textbox(placeholder="Input", label="User input")
                # model_output = gr.Textbox(label="Output", lines=10, interactive=False)
                model_output = gr.Markdown(label="Output", height=320, container=True, show_label=True)
                button_submit = gr.Button(value="Submit")

        params = [user_text]
        user_text.submit(ask, params, model_output)
        button_submit.click(ask, params, model_output)

        return gr.mount_gradio_app(app, demo, path="/chat")

app = FastAPI()
app = configure_gradio(app)
@app.get("/")
def root():
    return RedirectResponse(url="/chat")
@app.get("/working/{rest_of_path:path}")
def working(rest_of_path: str):
    full_path = "/working/" + rest_of_path
    return RedirectResponse(url=f"{target_url}{full_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
