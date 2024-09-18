# Evaluate Your AI App

## Overall

Evaluation is a critical process to measure the performance, quality, and effectiveness of AI apps. This guide will help you evaluate your AI apps and view the results in AI Toolkit.

## Run evaluation
### Step 1: Set up the Python environment

1. Ensure Python (with version equal to or greater than 3.8) is installed.
1. Install required libraries with the following command under project root:
   ```bash
   pip install -r ai-resource/evaluation/requirements.txt
   ```

### Step 2: Import your AI app as the evaluation target

Import your AI app into the script and wrap it in an evaluation target. The evaluation target is a function that takes a question and responds with an answer.

```python
def target_app(question):
   # import your AI app into the script and wrap it in an evaluation target, like:
   response = my_app(question)
   return { "answer": response.message }
```

### Step 3: Set up LLM for AI-assisted evaluator

Most of the built-in evaluators are AI-assisted:
- GroundednessEvaluator
- RelevanceEvaluator
- CoherenceEvaluator
- FluencyEvaluator
- SimilarityEvaluator

If one of those evaluators is selected, you need to set `model_config` with Azure OpenAI model.

> **Note**: `model_config` with OpenAI configuration isn't supported in the `promptflow-eval` SDK yet, but it's planed for version `v0.3.3`.
>

**Use Azure OpenAI Endpoint**:
1. Create an Azure OpenAI resource and deploy a model. Detailed instructions can be found in the [Azure OpenAI documentation](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource).
2. Set up the necessary environment variables in `.env` file, including the API endpoint, key and deployment name.
   ```python
   model_config = AzureOpenAIModelConfiguration(
     azure_endpoint=os.environ.get("EVALUATOR_MODEL_ENDPOINT"),
     api_key=os.environ.get("EVALUATOR_MODEL_API_KEY"),
     azure_deployment=os.environ.get("EVALUATOR_MODEL_NAME"),
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

## Additional

### Built-in evaluators

Here list the built-in evaluators from `promptflow-eval`SDK and the meaning of the metrics:

Name | What is this metric?
| - | - 
GroundednessEvaluator| Measures how well the model's generated answers align with information from the source data (user-defined context).
RelevanceEvaluator | Measures the extent to which the model's generated responses are pertinent and directly related to the given questions.
CoherenceEvaluator | Measures how well the language model can produce output that flows smoothly, reads naturally, and resembles human-like language.
FluencyEvaluator | Measures the grammatical proficiency of a generative AI's predicted answer.
SimilarityEvaluator | Measures the similarity between a source data (ground truth) sentence and the generated response by an AI model.
F1ScoreEvaluator | Measures the ratio of the number of shared words between the model generation and the ground truth answers.

For more details about how does these built-in evaluators work, refer to [the documentation](https://learn.microsoft.com/en-us/azure/ai-studio/concepts/evaluation-metrics-built-in?tabs=warning#prompt-only-based-groundedness).

## Reference
- [Evaluate with the prompt flow SDK](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/flow-evaluate-sdk)
* [Built-in evaluators](https://learn.microsoft.com/en-us/azure/ai-studio/concepts/evaluation-metrics-built-in?tabs=warning#prompt-only-based-groundedness)
