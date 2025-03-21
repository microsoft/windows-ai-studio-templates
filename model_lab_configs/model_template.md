# About Model Template

## Steps for onboarding a new model

If you are onboarding a model or update model version, please follow:

- If new model, go to `model_list.json`, add one or modify existing model status to ready.
- Create model folder with version: e.g. model_lab_configs\huggingface\google\vit-base-patch16-224\1. Navigate to this folder.
- Create olive config json file: e.g. vit-base-patch16-224.json. Also see [requirements](#olive-json-requirements).
- Create model_project.config. You only need to create this simple json:
    ```
    {
        "workflows": [
            {
                "name": "Convert to QNN",
                "file": "vit-base-patch16-224.json"
            }
        ]
    }
    ```
- Create olive config json config file: e.g. vit-base-patch16-224.json.config
    + Add parameters you need. Please refer parameter_template.json. You can contribute new parameter template to it.
    + You need to organize sections by yourselves.
    + For parameter detail, you need to either only write values for template part (the others will be filled with template default):
    ```
    "parameters": [
        {
            "template": {
                "template": "ActivationType",
                "path": "passes.OnnxQuantization.activation_type"
            }
        }
    ]
    ```
    + Or write all necessary values
    ```
    "parameters": [
        {
            "name": "Quantize Dataset",
            "type": "enum",
            "values": [
                "imagenet-1k"
            ],
            "path": "data_configs[0].load_dataset_config.data_name"
        }
    ]
    ```
- `python sanitize.py`. It will set up other values. See [parameters set by it](#parameters-that-set-by-sanitizepy)

## Parameters that set by sanitize.py

- model_list.json:
    + version: read from folder structure
- model_project.config
    + template, version, templateName: same as path
    + phases: read from olive config
    + modelInfo: copy from model_list
    + So only name and file is needed
- *.json.config
    + For parameter, we either set every needed property except template
    + Or set template name and properties different from template in template

## Olive json Requirements

- engine not used: place everything in the root
- output model use external weight
    + not decided yet
- separate different datasets
    + currently no check in sanitize.py