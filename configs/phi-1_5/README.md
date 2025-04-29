
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


### Model fine-tuning on Azure

Please make sure that you have created the Azure ML workspace according to the following directions:
https://learn.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources?view=azureml-api-2

Create Compute cluster using GPU nodes (https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-gpu?view=azureml-api-2):

https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?view=azureml-api-2&tabs=azure-studio

Setup "hf-token" in the Keyvault associated with the Azure ML workspace.
Get HuggingFace access token from your HuggingFace account. 
1. Get your Huggingface token string from Settings -> [Access Tokens](https://huggingface.co/settings/tokens). Please, make sure that your account has access to any gated model that you will access for finetuning.
2. Create or use an existing [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview). Assume the key vault is named `keyvault_name`. Add a new secret named `hf-token`, and set the value as the token from the first step. It is important to note that `hf-token` secret name is reserved specifically for Huggingface login. Do not use this name in this keyvault for other purpose.
3. Give the compute cluster access to the keyvault `keyvault_name` using the following instructions:
a. Create a managed identity for the compute cluster.
b. Give the compute cluster access to the keyvault `keyvault_name` using the following instructions:
https://learn.microsoft.com/en-us/azure/key-vault/general/assign-access-policy?tabs=azure-portal

Update finetuning/aml_config.json with correct values.

Once the workspace is opened in a dev container, open a terminal (the default path is project root).

```bash
az login
python finetuning/invoke_olive.py --azure --aml_config finetuning/aml_config.json
```

This will submit an AML job which can be monitored using the link printed by the program. After training finishes, the trained model can be downloaded from the outputs folder.


### Inference

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