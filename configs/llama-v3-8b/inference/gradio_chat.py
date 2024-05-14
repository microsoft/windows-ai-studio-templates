# Import necessary libraries
from threading import Thread
import argparse
import os
import torch
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TextIteratorStreamer
from utils import check_adapter_path, load_model, load_peft_model, load_tokenizer, get_device

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

# Function to run the text generation process
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

    user_text.submit(run_generation, [user_text, top_p, temperature, top_k, max_new_tokens], model_output)
    button_submit.click(run_generation, [user_text, top_p, temperature, top_k, max_new_tokens], model_output)

    demo.queue(max_size=32).launch(server_name="0.0.0.0", server_port=7860)
