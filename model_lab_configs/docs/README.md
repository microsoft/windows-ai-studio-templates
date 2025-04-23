# AITK Model Lab README

## Model project directory structure explanation
This directory contains information and conversion history of a model.

### Directory structure

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

### Structure description from top to bottom

#### Current model
The top level folder contains `model project name` and `model name`: microsoft/resnet-50

#### Model files
- `README.md` includes model details such as the model's task, performance metrics, and usage instructions.
- `model_project.config` contains project template settings. Some settings can be overridden to suit user needs.
- `requirements.txt` lists the dependencies required to run the workflow and the inference sample.

#### Cache folder
This folder stores cache files generated during workflow execution. These cached results can help accelerate repeated runs of the workflow.

You can delete this folder to free up space if it's no longer needed.

#### History folder/history_1(20250414_161046)/
The timestamp in the `history` folder name indicates the run time: April 14, 2025 at 16:10:46.

This folder contains all output files, including logs, metrics, and model artifacts. Models are saved in the `./model` subfolder.

## FAQ
### Q: How to run workflows without AITK?
A: Please refer: [doc](./README-without-AITK.md)

### Q: After creating a new model project, the new project's folder is not opened.
A: Please open model project folder in vscode. Model lab will load your project.

### Q: How to switch project?
A: Please close the folder in vscode. Open model projet folder you need.

### Q: It takes long time when first time running workflows?
A: This is by design. It may take 15~20 minutes for overall process, which including environment setup process. AITK model lab need to setup python environment and install dependency packages. Next time it will be much faster.

### Q: How to run inference_sample.ipynb?
A: Click **Select Kernel** at the top right of the window, then choose **Python Environment**.

Select the environment you want to use. We recommend using the Python environment we provide, located at `C:\Users\{user_name}\.aitk\bin\model_lab_runtime`. This environment already has the required dependencies installed.

The first time you run a notebook with a new kernel, you may be prompted to install **ipykernel**. Please follow the prompt to complete the installation.
