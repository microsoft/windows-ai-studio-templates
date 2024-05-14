# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import sys
import os

import torch
from utils import load_tokenizer, load_model, load_peft_model, get_last_folder_alphabetically, get_device
from promptflow import tool

class ChatBot:
    # Class attributes to hold the model and tokenizer. Initialized to None.
    m = None
    tok = None

    @staticmethod
    def init_model():
        # Only initializes the model if it has not already been initialized.
        if ChatBot.m is None or ChatBot.tok is None:
            # Define the model name and retrieve the latest model checkpoint.
            model_name = "../model-cache/meta-llama/Llama-v3-8b"
            adapters_name = "../models/qlora/qlora/gpu-cpu_model/adapter"

            # Logging the model loading process.
            print(f"Starting to load the model {model_name} into memory")

            # Load the tokenizer from the utility function.
            ChatBot.tok = load_tokenizer(model_name)

            # Load the model with the specified configuration from the utility function.
            ChatBot.m = load_model(model_name, torch.<compute_dtype>, '<quant_type>')
            
            # Load the PEFT model with the adapters from the utility function.
            ChatBot.m = load_peft_model(ChatBot.m, adapters_name)

            # Logging the successful model loading.
            print(f"Successfully loaded the model {model_name} into memory")

    @staticmethod
    def chat(prompt: str) -> str:
        # Ensure the model is initialized before trying to chat.
        ChatBot.init_model()

        # Define the template that formats the chat input.
        template = "<prompt_template>"
        
        # Retrieve the appropriate device for model computations.
        device = get_device()
        
        # Process the input with the tokenizer and move it to the correct device.
        inputs = ChatBot.tok(template.format(prompt), return_tensors="pt").to(device)

        # Generate the response using the model.
        outputs = ChatBot.m.generate(**inputs,
                                     max_new_tokens=1024,
                                     pad_token_id=ChatBot.tok.pad_token_id,
                                     eos_token_id=ChatBot.tok.eos_token_id)

        # Decode the generated tokens to a string and return.
        text = ChatBot.tok.batch_decode(outputs)[0]
        return text

# Decorator to expose the chat method as a standalone function.
@tool
def chat(prompt: str) -> str:
    # Invokes the chat method of ChatBot class with the given prompt.
    return ChatBot.chat(prompt)
