import os
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.evals.evaluators import CoherenceEvaluator, SimilarityEvaluator
from promptflow.evals.evaluate import evaluate
from dotenv import load_dotenv

load_dotenv()

cwd = os.path.dirname(os.path.abspath(__file__))

# define dataset paths
dataset = "dataset/new-dataset/dataset.jsonl"
dataset_path = os.path.join(cwd, f"../{dataset}")

# define evaluation result path
evaluation_name = "my_evaluation"
result_path = os.path.join(cwd, f"results/{evaluation_name}.json")
os.makedirs(os.path.dirname(result_path), exist_ok=True)

# define evaluators
model_config = AzureOpenAIModelConfiguration(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

similarity_evaluator = SimilarityEvaluator(model_config)
coherence_evaluator = CoherenceEvaluator(model_config)


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
        output_path=result_path,
    )
