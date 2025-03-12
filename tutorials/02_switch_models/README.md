# Tutorial 02: Explore Different Models

This tutorial builds on top of the [Craft Prompt](https://github.com/microsoft/windows-ai-studio-templates/tree/dev/tutorials/01_craft_prompt/README.md) tutorial that showcases how to how to switch to a different model in the AI Toolkit. The AI Toolkit provides a variety of models to choose from, allowing you to select the one that best fits your needs. This is particularly useful when you want to experiment with different models or when you need to switch to a different model provider for any reason.

> **Note:** AI Toolkit supports [multiple model providers](https://code.visualstudio.com/docs/intelligentapps/models#_find-a-model) including models hosted by GitHub and Publisher (OpenAI, Anthropic and Google etc) as well as using models running locally via ONNX or Ollama runtime. And you can even [bring your own models](https://code.visualstudio.com/docs/intelligentapps/models#_bring-your-own-models).


## What you will learn
- Experiment with different models in `Prompt Builder`
- `View Code` and update the app for the selected model

## Prerequisites
- Completed the [Craft Prompt](https://github.com/microsoft/windows-ai-studio-templates/tree/dev/tutorials/01_craft_prompt/README.md) tutorial
- Latest version of [Python](https://www.python.org/downloads/)
- [AI Toolkit extension](https://code.visualstudio.com/docs/intelligentapps/overview#_install-and-setup) for Visual Studio Code
- Anthropic API key (Or access to desired model providers such as Goggle)

## Getting started with the tutorial
In this section, you will experiment with different models in the Prompt Builder to find the one that best works for you.

### Step 1: Add a new model
1. Open Model Catalog in the AI Toolkit sidebar
2. Search for Claude in the catalog
![catalog](./images/catalog.png)
3. Click `Add` in the Claude 3.7 Sonnet model card
4. Enter the Claude API Key
![add_key](./images/enter_key.png)

You can refer to [this document](https://code.visualstudio.com/docs/intelligentapps/models) for more instructions on adding a model, such as using Ollama models.

### Step 2: Select and Test the Model in Prompt Builder
Load the model and prompt in `Prompt Builder` through [this VS Code URL](vscode://ms-windows-ai-studio.windows-ai-studio/open_prompt_builder?model_id=anthropic/claude-3-7-sonnet-20250219&&system_prompt_file=prompt.aitk.txt&&user_prompt=generate%20a%20question%20about%20Newton%27s%20Laws%20of%20Motion)

Alternatively, you can configure manually by following the steps below:
1. Open the **Prompt Builder** in the AI Toolkit sidebar
2. Select the Claude 3.7 model (Or the model you added)
![select-model](./images/select_model.png)
3. Copy the system prompt from [final_prompt.aitk.txt](./final_prompt.aitk.txt) we built from previous tutorial and input it.
4. Enter a user prompt to test the new model, for example: `Create an intermediate level mathematical question for a grade 8 student.`
5. Verify if the response works as expected.

### Step 3: Compare results
Now that you can run the same prompt against different models, you can compare them to find the one that best works for you:

| OpenAI GPT-4o | Anthropic Claude 3.7 Sonnet |
|----------|----------|
| ![openai](./images/openai.png)    | ![claude](./images/Claude.png)   |

### Step 4: Export code
Once you are satisfied with the response and decide to switch to Claude 3.7 model, you can export the code and update it in the console app we previously built.
1. Click `View Code` to open the code sample in VS Code editor.
2. Copy the code sample to the `chat` API in [final_app.py](./final_app.py).
3. Depending on your chosen model, install requirement Python package(s) and set the API key if needed.
![change-model](./images/anthropic_code.png)

## What's Next
To explore more tutorials, select the AI Toolkit view in the Activity Bar, then select **CATALOG** > **Tutorials** to open the tutorials recommended below:

- [Apply structured outputs](https://github.com/microsoft/windows-ai-studio-templates/tree/dev/tutorials/03_structured_output/README.md)
- [Bulk run prompts](https://github.com/microsoft/windows-ai-studio-templates/tree/dev/tutorials/04_run_prompts_in_batch/README.md)
- [Run evaluation](https://github.com/microsoft/windows-ai-studio-templates/tree/dev/tutorials/05_evaluate_prompt/README.md)