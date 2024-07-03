The `configs` folder contains configuration files used to resolve Mustache template defined in `models`.

There's three kinds of files defined in the `configs` folder:

- `projectSettings.json.mustache`: Mustache template consumed by scaffold workflow to render the configure-project WebView. Currently all fine-tuning models sharing the same projectSettings template. The value of the `defaultValue` property will be defined in a [{{ mustache }}](https://mustache.github.io/) variable since default value might vary between models. For example,

    ```json
    {
        "type": "String",
        "label": "Inference prompt template:",
        "info": "Prompt template used at inference time, make sure it matches the finetuned version.",
        "defaultValue": "{{promptTemplate}}"
    }
    ```

- `<model-name>\defaultProjectSettings.json`: The `{{ mustache }}` variables defined in [projectSettings.json.mustache](./projectSettings.json.mustache) will be resolved from this file. Each fine-tuning model has its own default values for the project settings.

    Behind the scenes, the WebView UI needs to display the default value for each configuration in the configure-project step. The generator will parse the `configs` sections and generate the data map used to render the template.

    ```json
    [
        {
            "groupId": "modelInference",
            "configs": {
                "condaEnvName": "llama-7b-env",
                "promptTemplate": "### Text: {}\\n### The tone is:\\n"
            }
        },
        {
            "groupId": "dataConfigs",
            "configs": {
                ...
            }
        },
        {
            "groupId": "modelFinetuning",
            "configs": {
                ...
            }
        }
    ]
    ```

- `<model-name>\templateInput.json`: In addition to project settings, additional input used to render the template can be placed in this folder. For example, all models share the common template `common\finetuningParameters.mustache`, but the fine-tuning commands differ. We can extract this dynamic part as a custom variable `{{finetuningCommands}}` and provide its value through `<model-name>\templateInput.json`:

    ```json
    {
        "finetuningCommands": [
            "cd /mount",
            "pip install huggingface-hub==0.22.2",
            "huggingface-cli download meta-llama/Llama-2-7b-hf --revision main --local-dir ./model-cache/meta-llama/Llama-2-7b --local-dir-use-symlinks False --cache-dir ./cache/hfdownload",
            "pip install -r ./setup/requirements.txt",
            "python3 ./finetuning/invoke_olive.py && find models/ -print | grep adapter/adapter"
        ],
        ...
    }
    ```