# Synthetic Data Generation

## Overall

Leveraging large language models(LLM) is a crucial technique in synthetic data generation, capable of producing high-quality, diverse, and privacy-compliant datasets. This approach can be applied in various scenarios, including training machine learning models, fine-tuning different language models, and conducting evaluation and testing, among others.

> **Important**: When using a large language model (LLM) to create datasets for developing other models, adherence to the relevant licensing agreements is essential.
>
> This document references Azure OpenAI and Phi-3 as examples. For more details, visit [Azure OpenAI](https://openai.com/policies/business-terms/) and [Phi-3](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/blob/main/LICENSE).

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

To set up your language model inference endpoint, you can use Azure OpenAI by default or configure it to use other model.

- **[Option 1]** Use Azure OpenAI Endpoint
  1. Create an Azure OpenAI resource and deploy a model. Detailed instructions can be found [here](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource).
  2. Configure environment variables

     Set up the necessary environment variables in the `generate_qa_dataset.py` script. This involves specifying the Azure OpenAI inference API endpoint and your API key.

      ```python
      # Define the Azure OpenAI inference API endpoint  
      api_endpoint = os.environ.get("API_ENDPOINT", "https://<your-resource-name>.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview") 

      # Define the Azure OpenAI API key in env variables
      api_key = os.environ.get("API_KEY")  
      ```

- **[Option 2]** Use the Local Model Inference Endpoint in AI Toolkit
  1. Execute the command palette `AI Toolkit: Download an inference model`.
  2. Choose a model to generate the dataset, e.g., `Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx`.
  3. Configure environment variables

     Set up the necessary environment variables in the `generate_qa_dataset.py` script. This involves specifying the local inference API endpoint and the model name.

      ```python
      # Define the inference API endpoint, the default is for the local API in AI Toolkit
      api_endpoint = os.environ.get("API_ENDPOINT", "http://127.0.0.1:5272/v1/chat/completions") 
      # Define the model to use for the request
      model = os.environ.get("MODEL", "Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx")
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
