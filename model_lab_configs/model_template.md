# About Model Template

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

## Where data should go

- If the data is not related to a specific olive json
    - we want to update it on-the-fly: model_list.json / parameter_template.json
    - on-the-fly is not needed: model_lab.workspace.config / model_project.config
- If the data is related to olive json
    + on-the-fly is needed: *.json.config
    + on-the-fly not needed: model_project.config
