# About Model Template

## Steps for onboarding a new model

If you are onboarding a model or update model version, please follow:

- If new model, go to `model_list.json`, add one or modify existing model status to ready.
- Create model folder with version: e.g. model_lab_configs\huggingface\google\vit-base-patch16-224\1. Navigate to this folder.
- Create olive config json file: e.g. vit-base-patch16-224.json. Also see [requirements](#olive-json-requirements).
    + For other files, please follow [folder structure](#folder-structure).
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

## Folder structure

These files should be placed in the root of the template folder:
- README.md
- requirements.txt
- inference_sample.ipynb
    + it will be shared for all olive configs. If needed.
- model_project.config

These files should be placed in the same folder with the olive json file (so olive json file could be placed in the sub folder):
- olive_config.json
- olive_config.json.config
- olive_config_inference_sample.ipynb
    + If needed
- user_script.py

At least one of inference_sample.ipynb or olive_config_inference_sample.ipynb should exist for each olive config.

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
- create .gitignore
- check requirements.txt
    + TODO set or check common dependencies 

## Olive json Requirements

- engine not used: place everything in the root
- output model use external weight
    + so ipynb could be used without change
- separate different datasets
- only one system is used
