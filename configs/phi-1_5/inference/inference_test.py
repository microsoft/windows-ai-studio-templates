import sys
import torch
from peft import PeftModel    

from promptflow import tool

from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer,BitsAndBytesConfig,TextStreamer

model_name = "model-cache/microsoft/phi-1_5"
adapters_name = "cache/models/<finetuned_adapters_file_path>"

# Check the current value of the variable
if adapters_name == "cache/models/<finetuned_adapters_file_path>":
    print("Please replace the <finetuned_adapters_file_path> with your adapter location.")
    sys.exit()

print(f"Starting to load the model {model_name} into memory")

tok = AutoTokenizer.from_pretrained(model_name, device_map='auto',trust_remote_code=True)

# set pad token
tok.add_special_tokens({'pad_token': '[PAD]'})

# Set the padding direction to the right
tok.padding_side = 'left'

m = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name,
        trust_remote_code=True,
        device_map='auto',
        torch_dtype=torch.<compute_dtype>,
        # 4-bit quantization configuration
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.<compute_dtype>,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type='<quant_type>'
        ),
    )

# Resize the embeddings bacuse of the PAD token
m.resize_token_embeddings(len(tok))

m = PeftModel.from_pretrained(m, adapters_name)

print(f"Successfully loaded the model {model_name} into memory")

template = "### Question: {}\n### Answer: \n"

device = "cuda:0"

user_input = ""
while True:
    new_input = input("Enter your text (type #end to stop): ")
    if new_input == "#end":
        break

    inputs = tok(template.format(new_input), return_tensors="pt").to(device)
    streamer = TextStreamer(tok)

    # Despite returning the usual output, the streamer will also print the generated text to stdout.
    _ = m.generate(**inputs, streamer=streamer, 
                # Generation Configuration
                   max_new_tokens=1024,
                   pad_token_id=tok.pad_token_id,
                   eos_token_id=tok.eos_token_id)
    
