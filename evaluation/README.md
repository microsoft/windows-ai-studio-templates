# Evaluate Your AI App

## Overall

Evaluation is a critical process to measure the performance, quality and effectiveness of AI apps. This guide will help you to evaluate your AI apps with the `promptflow-evals` SDK and view the results in AI Toolkit.

## Run evaluation
### Step 1: Set up the Python environment

Install required libraries with the following command under project root:
```bash
pip install -r ai-resource/evaluation/requirements.txt
```

### Step 2: Import your AI app as the evaluation target

Import your AI app in the script and then wrap it into evaluation target. The evaluation target is a function accepts question and return an object of answer.

```python
def target_app(question):
   # import your AI app and wrap it into the evaluation target, like:
   response = my_app(question)
   return { "answer": response.message }
```

### Step 3: Set up LLM information for AI-assisted evaluator

Most of the built-in evaluators are AI-assisted:
- GroundednessEvaluator
- RelevanceEvaluator
- CoherenceEvaluator
- FluencyEvaluator
- SimilarityEvaluator

If AI-assisted evaluator is selected, you need to set `model_config` with Azure OpenAI model.

> **Note**: `model_config` with OpenAI configuration is not supported for `promptflow-eval` SDK yet and it's planed to be supported in version `v0.3.3`.
>

**Use Azure OpenAI Endpoint**:
1. Create an Azure OpenAI resource and deploy a model. Detailed instructions can be found [here](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource).
2. Set up the necessary environment variables like API endpoint and key.
   ```python
   model_config = AzureOpenAIModelConfiguration(
     azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
     api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
     azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
   )
   ```

### Step 4: Run the script

Run evaluation with the following command under project root:
```bash
python -m ai-resource.evaluation.evaluate
```

## View evaluation result in VS Code

### Step 1: Run command palette AI Toolkit: View evaluations
Select `View` > `Command Palette` > `AI Toolkit: View evaluations`.
![image](https://github.com/user-attachments/assets/15de6c8f-e62d-40b6-a44b-a3d4be93ab62)

### Step 2: Select the evaluation result
Browse and select the evaluation result JSON file under `ai-resource/evaluation/results/`.


## Reference
- [Evaluate with the prompt flow SDK](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/flow-evaluate-sdk)