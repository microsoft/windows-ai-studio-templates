# About File Structure

After creating the model project and run several times, you could see the file structure like this:

```
model_project_name/
├── model_lab.workspace.config
└── huggingface_microsoft_resnet-50_v1/
    ├── .gitignore
    ├── imagenet.py
    ├── inference_sample.ipynb
    ├── model_project.config
    ├── README.md
    ├── requirements.txt
    ├── resnet_ptq_qnn.json
    ├── cache/
    └── history/
        └── history_1(20250414_161046)/
            ├── model/
            ├── footprints.json
            ├── history.config
            ├── history.config.user
            ├── inference_sample.ipynb
            ├── log.txt
            ├── metrics.json
            ├── model_config.json
            ├── olive_config.json
            └── run_history.txt
        └── history_2/
        └── history_3/
```
