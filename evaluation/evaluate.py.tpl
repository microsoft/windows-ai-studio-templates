import os
{{#llmProvider.OpenAI}}
from promptflow.core import OpenAIModelConfiguration
{{/llmProvider.OpenAI}}
{{#llmProvider.AzureOpenAI}}
from promptflow.core import AzureOpenAIModelConfiguration
{{/llmProvider.AzureOpenAI}}
from promptflow.evals.evaluators import *
from promptflow.evals.evaluate import evaluate
from dotenv import load_dotenv

load_dotenv()


# define dataset paths
dataset_path = "{{{datasetPath}}}"

# define evaluation result path
evaluation_name = "{{evaluationName}}"
cwd = os.path.dirname(os.path.abspath(__file__))
result_path = os.path.join(cwd, f"results/{evaluation_name}.json")
os.makedirs(os.path.dirname(result_path), exist_ok=True)

# define evaluators
{{#llmProvider.AzureOpenAI}}
model_config = AzureOpenAIModelConfiguration(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
)
{{/llmProvider.AzureOpenAI}}
{{#llmProvider.OpenAI}}
model_config = OpenAIModelConfiguration(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-3.5-turbo",
)
{{/llmProvider.OpenAI}}

{{#evaluators.CoherenceEvaluator}}
coherence_evaluator = CoherenceEvaluator(model_config)
{{/evaluators.CoherenceEvaluator}}
{{#evaluators.F1ScoreEvaluator}}
f1score_evaluator = F1ScoreEvaluator()
{{/evaluators.F1ScoreEvaluator}}
{{#evaluators.FluencyEvaluator}}
fluency_evaluator = FluencyEvaluator(model_config)
{{/evaluators.FluencyEvaluator}}
{{#evaluators.GroundednessEvaluator}}
groundedness_evaluator = GroundednessEvaluator(model_config)
{{/evaluators.GroundednessEvaluator}}
{{#evaluators.RelevanceEvaluator}}
relevance_evaluator = RelevanceEvaluator(model_config)
{{/evaluators.RelevanceEvaluator}}
{{#evaluators.SimilarityEvaluator}}
similarity_evaluator = SimilarityEvaluator(model_config)
{{/evaluators.SimilarityEvaluator}}


def target_app(question):
    # TODO: import your AI app and wrap it into the evaluation target, something like:
    # answer = my_app(question)
    # return { "answer": answer }
    raise NotImplementedError(
        "Please import your AI app and wrap it into the evaluation target."
    )


if __name__ == "__main__":
    # run evaluation
    evaluate(
        target=target_app,
        # file path to the dataset
        data=dataset_path,
        evaluators={
{{#evaluators.CoherenceEvaluator}}
            "coherence": coherence_evaluator,
{{/evaluators.CoherenceEvaluator}}
{{#evaluators.F1ScoreEvaluator}}
            "f1score": f1score_evaluator,
{{/evaluators.F1ScoreEvaluator}}
{{#evaluators.FluencyEvaluator}}
            "fluency": fluency_evaluator,
{{/evaluators.FluencyEvaluator}}
{{#evaluators.GroundednessEvaluator}}
            "groundedness": groundedness_evaluator,
{{/evaluators.GroundednessEvaluator}}
{{#evaluators.RelevanceEvaluator}}
            "relevance": relevance_evaluator,
{{/evaluators.RelevanceEvaluator}}
{{#evaluators.SimilarityEvaluator}}
            "similarity": similarity_evaluator,
{{/evaluators.SimilarityEvaluator}}
        },
        # column mapping
        evaluator_config={
            "default": {
{{#requiredColumnData.question}}
                "question": "${data.question}",
{{/requiredColumnData.question}}
{{#requiredColumnData.context}}
                "context": "${data.context}",
{{/requiredColumnData.context}}
{{#requiredColumnData.groundTruth}}
                "ground_truth": "${data.ground_truth}",
{{/requiredColumnData.groundTruth}}
{{#requiredColumnData.answer}}
                "answer": "${target.answer}",
{{/requiredColumnData.answer}}
            }
        },
        # output the evaluation result to a file
        output_path=result_path,
    )
