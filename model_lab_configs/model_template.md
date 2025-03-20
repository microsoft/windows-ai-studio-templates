# Parameters that set by sanitize.py
sanitize.py is a script that helps to generate all config files used by Model WorkSpace.

If you are onboarding a model or update model version, please follow:
1. If new model, go to `model_list.json`, modify model status to ready.
2. Create model folder with version: e.g. model_lab_configs\huggingface\google\vit-base-patch16-224\1. Navigate to this folder.
3. Create olive config json file: e.g. vit-base-patch16-224.json
4. Create model_project.config. You only need to create this simple json:
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
5. Create olive config json config file: e.g. vit-base-patch16-224.json.config

    Add parameters you need. Please refer parameter_template.json. You can contribute new parameter template to it.

    You need to organize sections by yourselves. But for parameter detail, you only need to provide simple json:

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
6. python sanitize.py

# Details about sanitize.py
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

# Olive json Requirements

- engine not used: place everything in the root
- output model use external weight ?
- separate different datasets
    + currently no check in sanitize.py
