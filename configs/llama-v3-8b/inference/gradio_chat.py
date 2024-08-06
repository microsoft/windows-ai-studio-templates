# Import necessary libraries
from threading import Thread
import argparse
import os
import torch
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TextIteratorStreamer
from utils import check_adapter_path, load_model, load_peft_model, load_tokenizer, get_device
from fastapi import FastAPI, HTTPException
from sse_starlette.sse import EventSourceResponse
import json
from pydantic import BaseModel, Field
from typing import List
import time
import uuid

# Create the parser
parser = argparse.ArgumentParser(description='Check model usage.')

# Add the arguments
parser.add_argument('--baseonly', action='store_true', 
                    help='A boolean switch to indicate base only mode')

# Execute the parse_args() method
args = parser.parse_args()

# Define model and adapter paths, data type, and quantization type
model_name = "../model-cache/meta-llama/Llama-v3-8b"
adapters_name = "../models/qlora/qlora/gpu-cpu_model/adapter"  # Ensure this path is correctly set before running
torch_dtype = torch.<compute_dtype>  # Set the appropriate torch data type
quant_type = '<quant_type>'  # Set the appropriate quantization type


# Display device and CPU thread information
print("Running on device:", get_device())
print("CPU threads:", torch.get_num_threads())

# Load model and tokenizer, and set up the model
check_adapter_path(adapters_name)
tokenizer = load_tokenizer(model_name)

model = load_model(model_name, torch_dtype, quant_type)
model.resize_token_embeddings(len(tokenizer))

usingAdapter = False
if os.path.exists(adapters_name) and not args.baseonly:
    usingAdapter = True
    model = load_peft_model(model, adapters_name)

device = get_device()

print(f"Model {model_name} loaded successfully on {device}")

class ChatCompletionsRequestMessage(BaseModel):
    role: str
    content: str

class ChatCompletionsRequest(BaseModel):
    stream: bool = Field(False)
    messages: List[ChatCompletionsRequestMessage]
    max_tokens: int = Field(256)
    temperature: float = Field(1)
    top_p: float = Field(1)

def calculate_token_count(tokenizer: AutoTokenizer, input: str):
    result = tokenizer(input)
    if 'input_ids' not in result:
        return 0
    return len(result['input_ids'])

# Host the model as an OpenAI chat completion compatible RESTful API
def inference_generator(request: ChatCompletionsRequest):
    template = "<prompt_template>"
    user_messages = list(filter(lambda m: m.role == "user", request.messages))
    if len(user_messages) == 0:
        raise HTTPException(status_code=400, detail="'messages' should contain at least 1 user message")
    input_message = user_messages[-1]

    prompt = template.format(input_message.content) if usingAdapter else input_message.content
    context_length = tokenizer.model_max_length
    input_token_count = calculate_token_count(tokenizer, prompt)
    
    print(f"Prompt: '{prompt}'")

    if request.max_tokens > 0:
        max_new_tokens = min(context_length - input_token_count, request.max_tokens)
    else:
        max_new_tokens = context_length - input_token_count

    model_inputs = tokenizer(prompt, return_tensors="pt")
    model_inputs = model_inputs.to(device)

    # Generate text in a separate thread
    streamer = TextIteratorStreamer(tokenizer, timeout=10., skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = dict(
        model_inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_p=request.top_p,
        temperature=request.temperature,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    t = Thread(target=model.generate, kwargs=generate_kwargs)
    t.start()

    event_id = str(uuid.uuid4())
    for new_text in streamer:
        event = {
            "id": event_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": os.path.basename(model_name),
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "content": new_text,
                    },
                    "logprobs": None,
                    "finish_reason":None
                }
            ]
        }

        data = json.dumps(event)
        yield dict(data=data)

def configure_api(app: FastAPI):
    @app.post("/v1/chat/completions")
    def chat_completion(request: ChatCompletionsRequest):
        # "\n" is the standard way but sse_starlette defaults to \r\n
        # https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#sending_events_from_the_server
        return EventSourceResponse(inference_generator(request), sep="\n")

# Host the model as a Gradio web app
def run_generation(user_text, top_p, temperature, top_k, max_new_tokens):
    template = "<prompt_template>"
    model_inputs = tokenizer(template.format(user_text) if usingAdapter else user_text, return_tensors="pt")
    model_inputs = model_inputs.to(device)

    # Generate text in a separate thread
    streamer = TextIteratorStreamer(tokenizer, timeout=10., skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = dict(
        model_inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_p=top_p,
        temperature=float(temperature),
        top_k=top_k,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    t = Thread(target=model.generate, kwargs=generate_kwargs)
    t.start()

    # Retrieve and yield the generated text
    model_output = ""
    for new_text in streamer:
        model_output += new_text
        yield model_output
    return model_output

def configure_gradio(app: FastAPI):
    # Gradio UI setup
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=4):
                user_text = gr.Textbox(placeholder="Write your question here", label="User input")
                model_output = gr.Textbox(label="Model output", lines=10, interactive=False)
                button_submit = gr.Button(value="Submit")

            with gr.Column(scale=1):
                max_new_tokens = gr.Slider(minimum=1, maximum=1000, value=250, step=1, label="Max New Tokens")
                top_p = gr.Slider(minimum=0.05, maximum=1.0, value=0.95, step=0.05, label="Top-p (nucleus sampling)")
                top_k = gr.Slider(minimum=1, maximum=50, value=50, step=1, label="Top-k")
                temperature = gr.Slider(minimum=0.1, maximum=5.0, value=0.8, step=0.1, label="Temperature")

        params = [user_text, top_p, temperature, top_k, max_new_tokens]
        user_text.submit(run_generation, params, model_output)
        button_submit.click(run_generation, params, model_output)

        return gr.mount_gradio_app(app, demo, path="/")

app = FastAPI()
configure_api(app)
app = configure_gradio(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)