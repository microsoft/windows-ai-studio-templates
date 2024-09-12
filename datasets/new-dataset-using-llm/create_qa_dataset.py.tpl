import os
import json
import re
import requests
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from dotenv import load_dotenv

# Set up the local inference API endpoint
load_dotenv()
api_endpoint = os.environ.get("API_ENDPOINT") 
api_key = os.environ.get("API_KEY")
model = os.environ.get("MODEL")

# Configuration for QA pair generation
qa_nums = 3
text = "Using large language models(LLM) is a crucial technique in synthetic data generation, capable of producing high-quality, diverse, and privacy-compliant datasets. This technique can be applied in different scenarios, including training machine learning models, fine-tuning different language models, and conducting evaluation and testing."
output_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "qa.jsonl"
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
    "max_tokens": 512,
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


# 5. Extract the question-answer pairs from the response
content = "".join(content_arr)
qnas = [
    {"question": question.strip(), "answer": answer.strip()}
    for question, answer, _ in re.findall(
        r"question:(.+?)answer:(.+?)(?=(question):|$)",
        content,
        flags=re.DOTALL,
    )
]

# 6. Convert the response to a DataFrame and save it to a JSONL file
df = pd.DataFrame(qnas)
df.to_json(output_file_path, orient='records', lines=True)
