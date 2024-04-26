
### Preparations

1. Make sure NVIDIA driver are installed in the host. 
2. Run `huggingface-cli login`, if you are using HF for dataset ustilization
3. `Olive` key settings explanations for anything that modifies memory usage. 

### Activate Conda
Since we ware using WSL environment and is shared you need to manually acitvate the conda environment. After this step you can run finetunning or inference.

```bash
conda activate [conda-env-name] 
```

### Base model fine-tuning only
To just try try the base model without fine-tuning you can run this command after activating conda.

```bash
cd inference

# Web browser interface allows to adjust a few parameters like max new token length, temperature and so on.
# User has to manually open the link (e.g. http://127.0.0.1:7860) in a browser after gradio initiates the connections.
python gradio_chat.py --baseonly
```

### Model fine-tuning and inferencing

Once the workspace is opened in a dev container, open a terminal (the default path is project root), then run the command below to fine tune a LLM on the selected dataset.

```bash
python finetuning/invoke_olive.py 
```

Checkpoints and final model will be saved in `models` folder.

Next run inferencing with the fune-tuned model through chats in a `console`, `web browser` or `prompt flow`.

```bash
cd inference

# Console interface.
python console_chat.py

# Web browser interface allows to adjust a few parameters like max new token length, temperature and so on.
# User has to manually open the link (e.g. http://127.0.0.1:7860) in a browser after gradio initiates the connections.
python gradio_chat.py
```

To use `prompt flow` in VS Code, please refer to this [Quick Start](https://microsoft.github.io/promptflow/how-to-guides/quick-start.html).