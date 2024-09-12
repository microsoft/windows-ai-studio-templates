# Synthetic Data Generation

## Overall

Using large language models(LLM) is a crucial technique in synthetic data generation, capable of producing high-quality, diverse, and privacy-compliant datasets. This technique can be applied in different scenarios, including training machine learning models, fine-tuning different language models, and conducting evaluation and testing.

> **Important**: When using a large language model (LLM) to create datasets for developing other models, it's important to follow the licensing agreements.
> This document mentions Azure OpenAI and Phi-3 as examples. For more details, visit [Azure OpenAI](https://openai.com/policies/business-terms/) and [Phi-3](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/blob/main/LICENSE).
>
> For example, if you opt for the default Azure OpenAI service, it's imperative to comply with OpenAI's licensing terms, which include specific restrictions such as:
>> What you cannot do:
>> Use Output to develop models that compete with OpenAI.


## Benefits of synthetic data

- Privacy Protection

  Synthetic data mimics real data without including sensitive information, making it perfect for fields with strict privacy rules.

- Structured and Easy to Use

  Synthetic data is often well-structured and can come pre-labeled, simplifying data preparation for machine learning.

- Data Augmentation

  It can fill gaps in sparse datasets, making them richer and more diverse, which is useful for balancing datasets.

- Unlimited Data Creation

  You can create synthetic data on-demand and at a large scale, providing a cost-effective way to obtain more training data.

- Bias Reduction

  Synthetic data can help reduce bias in AI models by balancing out biased datasets, leading to fairer AI systems.

## Create a synthetic dataset

**Step 1: Set up the Python Environment**

Install the required Python packages:

```sh
pip install -r requirements.txt
```

**Step 2: Prepare Your Inference Endpoint**

To set up your language model inference endpoint, you can use Azure OpenAI by default or configure it to use other model.

- **[Option 1]** Use the Local Model Inference Endpoint in AI Toolkit
  1. Run the command palette `AI Toolkit: Download an inference model`.
  2. Choose a model to create the dataset, e.g., `Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx`.
  3. Configure environment variables

     Set up the necessary environment variables in the `.env` file. This involves specifying the local inference API endpoint and the model name.

      ```
      # Define the inference API endpoint, the default is for the local API in AI Toolkit
      API_ENDPOINT=http://127.0.0.1:5272/v1/chat/completions
      # Define the model to use for the request
      MODEL=Phi-3-mini-4k-cpu-int4-rtn-block-32-acc-level-4-onnx"
      ```

- **[Option 2]** Use Azure OpenAI Endpoint
  1. Create an Azure OpenAI resource and deploy a model. Detailed instructions can be found [here](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource).
  2. Configure environment variables

     Set up the necessary environment variables in the `.env` file. This involves specifying the Azure OpenAI inference API endpoint and your API key.

      ```
      # Define the Azure OpenAI inference API endpoint
      API_ENDPOINT=https://<your-resource-name>.openai.azure.com/openai/deployments/<your-deployment-name>/chat/completions?api-version=<api-version>
      # Define the model to use for the request
      API_KEY=<your-api-key>
      ```

**Step 3: Update the Context for QA Sets**

Update the context within the script as needed to create the QA sets.

```python
# Configuration for QA pair generation
qa_nums = 5
text = "<your-context>"
```

**Step 4: Run the script**

Run the script to create the synthetic dataset:

```sh
python create_qa_dataset.py
```

The created synthetic dataset will be saved in `qa.jsonl`.
