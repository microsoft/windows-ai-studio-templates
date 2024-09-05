import os
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.evals.evaluators import CoherenceEvaluator,SimilarityEvaluator
from promptflow.evals.evaluate import evaluate
from dotenv import load_dotenv
load_dotenv()

dataset_path = "data/dataset1.jsonl"
evaluation_name = "my_evaluation"

# define evaluators
model_config = AzureOpenAIModelConfiguration(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

similarity_evaluator = SimilarityEvaluator(model_config)
coherence_evaluator = CoherenceEvaluator(model_config)

def target_app(question):
    # TODO: wrap your AI app into the evaluation target, something like:
    # answer = my_app(question)
    # return { "answer": answer }
    raise NotImplementedError("Please wrap your AI app into the evaluation target.")

if __name__ == "__main__":
    # run evaluation
    result_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        f"evaluation/results/{evaluation_name}.jsonl"
    )
    evaluate(
        target=target_app,
        # file path to the dataset
        data=dataset_path,
        evaluators={
            "similarity": similarity_evaluator,
            "coherence": coherence_evaluator,
        },
        # column mapping
        evaluator_config={
            "default": {
                "question": "${data.question}",
                "ground_truth": "${data.ground_truth}",
                "answer": "${target.answer}",
            }
        },
        # output the evaluation result to a file
        output_path=result_path
    )
