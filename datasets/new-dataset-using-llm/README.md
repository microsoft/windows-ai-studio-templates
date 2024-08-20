# Synthetic Data Generation
## Overall
Leveraging large language models(LLM) is a crucial technique in synthetic data generation, capable of producing high-quality, diverse, and privacy-compliant datasets. This approach can be applied in various scenarios, including training machine learning models, fine-tuning different language models, and conducting evaluation and testing, among others.

> Note: If you are using an LLM to generate a dataset for fine-tuning another model, please ensure you adhere to the relevant licenses.

## Benefits of synthetic data
- Privacy Protection

  Synthetic data mimics real data without including sensitive information, making it perfect for fields with strict privacy rules.

- Structured and Easy to Use

  Synthetic data is often well-structured and can come pre-labeled, simplifying data preparation for machine learning.

- Data Augmentation

  It can fill gaps in sparse datasets, making them richer and more diverse, which is useful for balancing datasets.

- Unlimited Data Generation

  You can generate synthetic data on-demand and at a large scale, providing a cost-effective way to get more training data.

- Bias Reduction

  Synthetic data can help reduce bias in AI models by balancing out biased datasets, leading to fairer AI systems.

## Generate a synthetic dataset
**Step 1: Setup the Python Environment**

Install the required Python packages:
```sh
pip install -r requirements.txt
```

**Step 2: Prepare Your Inference Endpoint**

You have two options to set up your language model inference endpoint.

- **[Option 1]** Use the Local Model Inference Endpoint in AI Toolkit
  1. Execute the command palette `AI Toolkit: Download an inference model`.
  2. Choose a model to generate the dataset, e.g., `Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx`.
  3. Set up the environment variables in `generate_qa_dataset.py`:
      ```python
      # Define the inference API endpoint, the default is for the local API in AI Toolkit
      api_endpoint = os.environ.get("API_ENDPOINT", "http://127.0.0.1:5272/v1/chat/completions") 
      # Define the model to use for the request
      model = os.environ.get("MODEL", "Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx")
      ```
- **[Option 2]** Use Azure OpenAI Endpoint
  1. Create an Azure OpenAI resource.
  2. Set up the environment variables in `generate_qa_dataset.py`:
      ```python
      # Define the Azure OpenAI inference API endpoint  
      # e.g., https://<your-resource-name>.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview  
      api_endpoint = os.environ.get("API_ENDPOINT")  

      # Define the Azure OpenAI API key
      api_key = os.environ.get("API_KEY")  
      ```

**Step 3: Update the Context for QA Sets**

Update the context within the script as needed to generate the QA sets.

```python
# Configuration for QA pair generation
qa_nums = 5
text = "<your-context>"
```

**Step 4: Run the script**

Run the script to generate the synthetic dataset:

```sh
python generate_qa_dataset.py
```
The generated synthetic dataset will be saved in `qa.jsonl`.