# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import sys

import torch
from utils import (load_tokenizer, load_model, load_peft_model, get_device, 
                   generate_text, run_prompt, check_adapter_path)

def main(model_name, adapters_name, torch_dtype, quant_type):
    """
    The main execution function that loads the model, tokenizer, and runs the prompt.
    Args:
    model_name (str): The name of the model to load.
    adapters_name (str): Path to the adapters file.
    torch_dtype (torch.dtype): The data type for model weights (e.g., torch.bfloat16).
    quant_type (str): The quantization type to use.
    """
    check_adapter_path(adapters_name)
    tokenizer = load_tokenizer(model_name)

    model = load_model(model_name, torch_dtype, quant_type)
    model.resize_token_embeddings(len(tokenizer))
    
    model = load_peft_model(model, adapters_name)
    device = get_device()
    model.to(device)
    print(f"Model {model_name} loaded successfully on {device}")
    template = "<prompt_template>"
    run_prompt(model, tokenizer, device, template)

if __name__ == "__main__":
    model_name = "../model-cache/meta-llama/Llama-v3-8b"
    adapters_name = "../models/qlora/qlora/gpu-cpu_model/adapter"  # Ensure this path is correctly set before running
    torch_dtype = torch.<compute_dtype>  # Set the appropriate torch data type
    quant_type = '<quant_type>'  # Set the appropriate quantization type

    try:
        main(model_name, adapters_name, torch_dtype, quant_type)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
