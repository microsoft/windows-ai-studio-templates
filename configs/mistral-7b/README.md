# Overview
This project is created by the AI Toolkit for VSCode. The toolkit simplifies generative AI app development by bringing together AI development tools and models from Azure AI Studio Catalog and other catalogs like Hugging Face. You will be able to fine-tune, test, and inference the models either locally or on a remote Azure Container App.
- [Local Development](#local-development)
    - [Preparations](#preparations)
    - [Activate Conda](#activate-conda)
    - [Base model fine-tuning only](#base-model-fine-tuning-only)
    - [Model fine-tuning and inferencing](#model-fine-tuning-and-inferencing)
- [Remote Development](#remote-development)
    - [Prerequisites](#prerequisites)
    - [Provision Azure Resources](#provision-azure-resources)
    - [Add Huggingface Token to the Azure Container App Secret](#add-huggingface-token-to-the-azure-container-app-secret)
    - [Run Fine-tuning](#run-fine-tuning)
    - [Provision Inference Endpoint](#provision-inference-endpoint)
    - [Deploy the Inference Endpoint](#deploy-the-inference-endpoint)
    - [Advanced usage](#advanced-usage)

## Local Development
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
# User has to manually open the link (e.g. http://0.0.0.0:7860) in a browser after gradio initiates the connections.
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


## Remote Development
### Prerequisites
1. To run the model fine-tuning in your remote Azure Container App Environment, make sure your subscription has enough GPU capacity. Submit a [support ticket](https://azure.microsoft.com/support/create-ticket/) to request the required capacity for your application. [Get More Info about GPU capacity](https://learn.microsoft.com/en-us/azure/container-apps/workload-profiles-overview)
2. Make sure you have a [HuggingFace account](https://huggingface.co/) and [generate an access token](https://huggingface.co/docs/hub/security-tokens)
3. Accept the LICENSE of [Mistral](https://huggingface.co/mistralai/Mistral-7B-v0.1) on HuggingFace. 

### Provision Azure Resources
To get started, you need to provision the Azure Resource for remote fine-tuning. Do this by running the `AI Toolkit: Provision Azure Container Apps job for fine-tuning` from the command palette.

Monitor the progress of the provision through the link displayed in the output channel.

### Add Huggingface Token to the Azure Container App Secret
If you're using Mistral, ensure to accept the LICENSE of [Mistral](https://huggingface.co/mistralai/Mistral-7B-v0.1) on HuggingFace. 
Following this, set your HuggingFace token as an environment variable to avoid the need for manual login on the Hugging Face Hub.
You can do this using the `AI Toolkit: Add Azure Container Apps Job secret for fine-tuning command`. With this command, you can set the secret name as [`HUGGING_FACE_HUB_TOKEN`](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables#hftoken) and use your Hugging Face token as the secret value.

### Run Fine-tuning
To start the remote fine-tuning job, execute the `AI Toolkit: Run fine-tuning` command.

To view the system and console logs, you can visit the Azure portal using the link in the output panel (more steps at [View and Query Logs on Azure](https://aka.ms/ai-toolkit/remote-provision#view-and-query-logs-on-azure)). Or, you can view the console logs directly in the VSCode output panel by running the command `AI Toolkit: Show the running fine-tuning job streaming logs`. 
> **Note:** The job might be queued due to insufficient resources. If the log is not displayed, execute the `AI Toolkit: Show the running fine-tuning job streaming logs` command, wait for a while and then execute the command again to re-connect to the streaming log.
    
During this process, QLoRA will be used for fine-tuning, and will create LoRA adapters for the model to use during inference.
The results of the fine-tuning will be stored in the Azure Files.

### Provision Inference Endpoint
After the adapters are trained in the remote environment, use a simple Gradio application to interact with the model.
Similar to the fine-tuning process, you need to set up the Azure Resources for remote inference by executing the `AI Toolkit: Provision Azure Container Apps for inference` from the command palette. 
   
By default, the subscription and the resource group for inference should match those used for fine-tuning. The inference will use the same Azure Container App Environment and access the model and model adapter stored in Azure Files, which were generated during the fine-tuning step. 


### Deploy the Inference Endpoint
If you wish to revise the inference code or reload the inference model, please execute the `AI Toolkit: Deploy for inference` command. This will synchronize your latest code with Azure Container App and restart the replica.  

Once deployment is successfully completed, you can access the inference API by clicking on the "*Go to Inference Endpoint*" button displayed in the VSCode notification. Or, the web API endpoint can be found under `ACA_APP_ENDPOINT` in `./infra/inference.config.json` and in the output panel. You are now ready to evaluate the model using this endpoint.

### Advanced usage
For more information on remote development with AI Toolkit, refer to the [Fine-Tuning models remotely](https://aka.ms/ai-toolkit/remote-provision) and [Inferencing with the fine-tuned model](https://aka.ms/ai-toolkit/remote-inference) documentation.