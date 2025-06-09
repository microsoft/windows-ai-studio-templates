# Get started with adding new template

A detailed guide to add a new template for AITK Model Lab.

## Add the new model to the list

First, the model needs to be added to the `model_list.json` to be ready to be shown.

The format is like

```
{
    "displayName": "google/vit-base-patch16-224",
    "icon": "gemini",
    "modelLink": "https://huggingface.co/google/vit-base-patch16-224",
    "id": "huggingface/google/vit-base-patch16-224",
    "runtimes": [
        "QNN",
        "AMDNPU",
        "IntelNPU"
    ],
    "architecture": "Transformer",
    "status": "Ready",
    "version": 1
}
```

Explanation for each field:

- displayName: display name
- icon: one of the `IconEnum` in `scripts\sanitize.py`. To add a new icon, please submit issue.
- modelLink: the link in the Huggingface
- id: the path to find the template
- runtimes: indicate what is supported for searching
- architecture: for searching
- status: `Ready` to be shown up.
- version: this will be set by `scripts\sanitize.py` from the folder structure

## Create the folder and put templates here

Create new folder following the id plus the version number like `model_lab_configs\huggingface\google\vit-base-patch16-224\1` and then put your files here like

- vit-base-patch16-224_qdq_qnn.json: required. The olive config. For requirements, see [OliveJsonRequirements.md](./OliveJsonRequirements.md)
- vit-base-patch16-224.py: optional. User script if needed
- .gitignore: optional. If you want to bring your own, please make sure it convers `requirements.md`
- README.md: required
- requirements.txt: optional. If exist, it will be installed after runtime requirements 
- inference_sample.ipynb: required. We should guide user how to use the model in WinML
    + This one will be used for olive json. If you want to provide a specific one, you could create one like `vit-base-patch16-224_qdq_qnn_inference_sample.ipynb`

## Create the model_project.config

This file tells the Model Lab which json should be treated as workflow and checked. It usually like this:

```
{
    "workflows": [
        {
            "name": "Convert to QNN",
            "file": "vit-base-patch16-224_qdq_qnn.json",
            "template": "huggingface/google/vit-base-patch16-224",
            "version": 1,
            "templateName": "vit-base-patch16-224_qdq_qnn"
        }
    ],
    "modelInfo": {
        "id": "huggingface/google/vit-base-patch16-224"
    }
}
```

Explanation for each field:

- name: display name
- file: the olive json config
- template / version /templateName: automatically set from file path
- modelInfo - id: automatically set. Used for the model card

## Create the *.json.config



