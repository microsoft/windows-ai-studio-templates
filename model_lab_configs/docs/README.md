# Folder structure explanation
This directory contains the conversion history for a model.

## Directory Structure

```
model_project_name/
└── huggingface_microsoft_resnet-50_v1/
    ├── README.md
    ├── model_project.config
    ├── requirements.txt
    ├── cache/
    └── history/
        └── history_1(20250414_161046)/
        └── history_2/
        └── history_3/
```

## Description

### Current Model
The top level folder contains `model project name` and `model name`: microsoft/resnet-50

### Model files
- `README.md` includes model details such as the model's task, performance metrics, and usage instructions.
- `model_project.config` contains project template settings. Some settings can be overridden to suit user needs.
- `requirements.txt` lists the dependencies required to run the workflow and the inference sample.

### Cache folder
This folder stores cache files generated during workflow execution. These cached results can help accelerate repeated runs of the workflow.

You can delete this folder to free up space if it's no longer needed.

### History folder/history_1(20250414_161046)/
The timestamp in the `history` folder name indicates the run time: April 14, 2025 at 16:10:46.

This folder contains all output files, including logs, metrics, and model artifacts. Models are saved in the `./model` subfolder.

# FAQ
## Q: How to run workflows without AITK?
A: Please refer: [doc](./README-without-AITK.md)

## Q: After creating a new model project, the new project's folder is not opened.
A: Please open model project folder in vscode. Model lab will load your project.

## Q: How to switch project?
A: Please close the folder in vscode. Open model projet folder you need.
