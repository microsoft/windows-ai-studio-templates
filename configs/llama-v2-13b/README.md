
### Preparations

1. Make sure NVIDIA driver are installed in the host. 
2. Run `huggingface-cli login`, if you are using HF for dataset ustilization
3. `Olive` key settings explanations for anything that modifies memory usage. 

### Model fine-tuning and inferencing

Once the workspace is opened in a dev container, open a terminal (the default path is project root), then run the command below to fine tune a LLM on the selected dataset.

```bash
python finetuning/invoke_olive.py 
```

Checkpoints and final model will be saved in `models` folder.

Next run inferencing with the fune-tuned model.

```bash
cd inference
python inference_test.py
```