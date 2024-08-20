import os
import json
import re
import requests
from jinja2 import Environment, FileSystemLoader
import pandas as pd

# Setup the local inference API endpoint
# [Option 1] Use the local API in AI Toolkit
api_endpoint = os.environ.get("API_ENDPOINT", "http://127.0.0.1:5272/v1/chat/completions") 
api_key = os.environ.get("API_KEY", None)
model = os.environ.get("MODEL", "Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx")

# [Option 2] Use the OpenAI API
# api_endpoint = os.environ.get("API_ENDPOINT", "https://<your-resource-name>.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview") 
# api_key = os.environ.get("API_KEY", "<your-api-key>")
# model = os.environ.get("MODEL", None)

# Configuration for QA pair generation
qa_nums = 3
text = "Leveraging large language models is a crucial technique in synthetic data generation, capable of producing high-quality, diverse, and privacy-compliant datasets. This approach can be applied in various scenarios, including training machine learning models, fine-tuning different language models, and conducting evaluation and testing, among others."
output_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "qa.csv"
) 

# 1. Load the prompt template
env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
template = env.get_template("prompt/qa.prompt").render(text=text, num_queries=qa_nums)

# 2. Generate prompt messages
messages = [
    {"role": role, "content": content.strip()}
    for role, content, _ in re.findall(
        r"(system|user|assistant):(.+?)(?=(system|user|assistant):|$)",
        template,
        flags=re.DOTALL,
    )
]

# 3. Payload for the request
payload = {
    "model": model,
    "messages": messages,
    "temperature": 1,
    "top_p": 1,
    "max_tokens": 1000,
    "stream": True,
}
headers = {"api-key": api_key} if api_key else {}

# 4. Send request to the Inference API
content_arr = []
with requests.post(
    api_endpoint, headers=headers, json=payload, stream=True
) as response:
    response.raise_for_status()
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: ") and line[6:] != "[DONE]":
            for choice in json.loads(line[6:]).get("choices", []):
               content_arr.append(choice.get("delta", {}).get("content", ""))
               print(content_arr[-1], end="")

# 5. Convert the response to a DataFrame and save it to a JSONL file
content = "".join(content_arr)
df = pd.DataFrame(json.loads(content))
df.to_csv(output_file_path, index=False)
