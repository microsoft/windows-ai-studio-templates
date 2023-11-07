import sys
import os
import re

import torch
from peft import PeftModel    
from promptflow import tool

from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer,BitsAndBytesConfig,TextStreamer

class ChatBot:
    m = None
    tok = None

    @staticmethod
    def init_model():
        if ChatBot.m is None or ChatBot.tok is None:
            model_name = "../model-cache/microsoft/phi-1_5"
            last_model_checkpoint = ChatBot.get_last_folder_alphabetically("../cache/models")
            adapters_name = os.path.join(last_model_checkpoint, "output_model", "adapter")

            # Code to initialize ChatBot.m and ChatBot.tok
            print(f"Starting to load the model {model_name} into memory")

            ChatBot.tok = AutoTokenizer.from_pretrained(model_name, device_map='auto', trust_remote_code=True)
            ChatBot.tok.add_special_tokens({'pad_token': '[PAD]'})
            ChatBot.tok.padding_side = 'left'

            ChatBot.m = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=model_name,
                trust_remote_code=True,
                device_map='auto',
                torch_dtype=torch.bfloat16,
                quantization_config=BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type='nf4'
                ),
            )

            ChatBot.m.resize_token_embeddings(len(ChatBot.tok))
            ChatBot.m = PeftModel.from_pretrained(ChatBot.m, adapters_name)

            print(f"Successfully loaded the model {model_name} into memory")
            
    @staticmethod
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]
    
    @staticmethod
    def get_last_folder_alphabetically(directory_path):
        if not os.path.exists(directory_path):
            return "Directory does not exist."

        all_files_and_folders = os.listdir(directory_path)

        # Filter out only directories
        only_folders = [f for f in all_files_and_folders if os.path.isdir(os.path.join(directory_path, f))]

        if not only_folders:
            return "No folders found in the directory."

        # Sort them using natural sort
        only_folders.sort(key=ChatBot.natural_sort_key)
        
        # Get the last folder alphabetically
        last_folder = only_folders[-1]

        return os.path.join(directory_path, last_folder)

    @staticmethod
    def chat(prompt: str) -> str:
        ChatBot.init_model()

        template = "### Question: {}\n### Answer: \n"
        device = "cuda:0"
        inputs = ChatBot.tok(template.format(prompt), return_tensors="pt").to(device)

        outputs = ChatBot.m.generate(**inputs,
                                      max_new_tokens=1024,
                                      pad_token_id=ChatBot.tok.pad_token_id,
                                      eos_token_id=ChatBot.tok.eos_token_id)

        text = ChatBot.tok.batch_decode(outputs)[0]
        return text

@tool
def chat(prompt: str) -> str:
    return ChatBot.chat(prompt)
