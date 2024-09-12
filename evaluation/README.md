# Evaluate your AI app

## Steps to run evaluation

1. Install required libraries with the following command under project root:
   ```bash
   pip install -r ai-resource/evaluation/requirements.txt
   ```
1. Import your AI app and wrap it into evaluation target (a function named `target_app` in the script). 
1. If AI-assisted evaluator is selected, set language model's api key in the `.env` file or environment variable.
1. Run evaluation with the following command under project root:
   ```bash
   python -m ai-resource.evaluation.evaluate
   ```

## View evaluation result

In VS Code:
1.	Select `View` > `Command Palette` > `AI Toolkit: View evaluations`.
    ![image](https://github.com/user-attachments/assets/15de6c8f-e62d-40b6-a44b-a3d4be93ab62)
1.	Browse and select the evaluation results JSON file under `ai-resource/evaluation/results/`.
