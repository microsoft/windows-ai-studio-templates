import os
import pandas as pd

# Replace this dataset with your own
dataset = [
    {
        "question": "When was the first version of Python released?",
        "answer": "The first version of Python, Python 0.9.0, was released in 1991.",
    },
    {
        "question": "Who created Python?",
        "answer": "Python was created by Guido van Rossum.",
    },
    {
        "question": "What type of programming language is Python?",
        "answer": "Python is a high-level, general-purpose programming language.",
    },
]

# Convert dataset to DataFrame
df = pd.DataFrame(dataset)

# Save DataFrame to JSONL
basePath = os.path.dirname(os.path.abspath(__file__))
jsonl_path = os.path.join(basePath, "dataset.jsonl")
df.to_json(jsonl_path, orient='records', lines=True)
