### Use Windows AI Studio to fine-tune the model remotely.
#### Prerequisites
To run the model fine-tuning in your remote Azure Container App Environment, you will need:
- [Windows AI Studio Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)
- Make sure your subscription have enough GPU capacity amount. Submit a [support ticket](https://azure.microsoft.com/support/create-ticket/) to request the capacity amount required for your application. [Learn More about GPU capacity](https://learn.microsoft.com/en-us/azure/container-apps/workload-profiles-overview)


#### Provision Azure Resources for Fine-tuning
In the `./infra` folder, you'll find templates for provisioning Azure resources. To provision new Azure resources for fine-tuning, execute the Command Palette `Windows AI Studio Tools: Provision Azure Container Apps job for fine-tuning`.

##### Configure Existing Azure Resources
If you already have Azure resources and need to configure them for fine-tuning, simply specify their names in `./infra/finetuning.parameters.json` file, then execute the Command Palette `Windows AI Studio Tools: Provision Azure Container Apps job for fine-tuning`. The specified resources will be updated and the others will be created.

For example, if you have an existing Azure container environment, the `./infra/finetuning.parameters.json` will be

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
      ...
      "acaEnvironmentName": {
        "value": "<your-aca-env-name>"
      },
      "acaEnvironmentStorageName": {
        "value": null
      },
      ...
    }
  }
```

##### Manual Configuration
If you've created and configured all the Azure resources without using the *Windows AI Studio Visual Studio Code Extension* command palette, you can fill in the resource names in `finetune.config.json` instead of running the provision command palette. For example,
```json
{
  "SUBSCRIPTION_ID": "<your-subscription-id>",
  "RESOURCE_GROUP_NAME": "<your-resource-group-name>",
  "STORAGE_ACCOUNT_NAME": "<your-storage-account-name>",
  "FILE_SHARE_NAME": "<your-file-share-name>",
  "ACA_JOB_NAME": "<your-aca-job-name>",
  "COMMANDS": [
    "cd /mount",
    "pip install -r ./setup/requirements.txt",
    "git lfs install",
    "git clone https://huggingface.co/microsoft/phi-1_5 ./model-cache/microsoft/phi-1_5",
    "python3 ./finetuning/invoke_olive.py"
  ]
}
```

#### Run Fine-tuning Job
Execute `Windows AI Studio Tools: Run fine-tuning` to initiate the fine-tuning job remotely. You can monitor its status in the Azure portal.

#### Provision Azure Resource for inference API
To provision new Azure resources for inference, use the Command Palette and select `Windows AI Studio Tools: Provision Azure Container Apps for inferencing`.

Similar to Fine-tuning, if you already have existing Azure resources, update `./infra/inferencing.parameters.json` before executing the provision command palette.

Alternatively, if you prefer not to use the provision command palette and deploy the Bicep file `inferencing.bicep` manually, you can specify your resource names in `inference.config.json`.


## Local Run
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
