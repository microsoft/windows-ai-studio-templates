import torch
from peft import PeftModel    

from transformers import AutoModelForCausalLM, LlamaTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer,BitsAndBytesConfig,TextStreamer

model_name = "model-cache/meta-llama/Llama-2-7b-hf"
adapters_name = "<adapters_file_path>"

print(f"Starting to load the model {model_name} into memory")

tok = LlamaTokenizer.from_pretrained(model_name, device_map='auto',skip_special_tokens=True )

# set pad token
tok.add_special_tokens({'pad_token': '[PAD]'})

# Set the padding direction to the right
tok.padding_side = 'left'

m = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name,
        device_map='auto',
        torch_dtype=torch.bfloat16,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type='nf4'
        ),
    )

#Resize the embeddings
m.resize_token_embeddings(len(tok))

m = PeftModel.from_pretrained(m, adapters_name)

print(f"Successfully loaded the model {model_name} into memory")

template = "### Question: {}\n### Answer:\n"

device = "cuda:0"

user_input = ""
while True:
    new_input = input("Enter your text (type #end to stop): ")
    if new_input == "#end":
        break

    inputs = tok(template.format(new_input), return_tensors="pt").to(device)
    streamer = TextStreamer(tok)

    # Despite returning the usual output, the streamer will also print the generated text to stdout.
    _ = m.generate(**inputs, streamer=streamer, max_new_tokens=1024, pad_token_id = tok.pad_token_id)
    
