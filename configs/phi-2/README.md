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
To run the model fine-tuning in your remote Azure Container App Environment, you need to make sure your subscription have enough GPU capacity amount. Submit a [support ticket](https://azure.microsoft.com/support/create-ticket/) to request the capacity amount required for your application. [Learn More about GPU capacity](https://learn.microsoft.com/en-us/azure/container-apps/workload-profiles-overview)

### Provision Azure Resources
To get started, you need provision the Azure Resource for remote fine-tuning. This can be done by running the `AI Toolkit: Provision Azure Container Apps job for fine-tuning.` from command palette.

You can monitor the progress of the provision via the link that is displayed in the output channel.

### [Optional] Add Huggingface Token to the ACA Secret
If you're using private HuggingFace dataset, you should set your HuggingFace token as an environment variable to bypass the need for manual login on the Hugging Face Hub.
You can do this using the `AI Toolkit: Add Azure Container Apps Job secret for fine-tuning command`. With this command, you can set the secret name as [`HUGGING_FACE_HUB_TOKEN`](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables#hftoken) and use your Hugging Face token as the secret value.

### Run Fine-tuning
To start the remote fine-tuning job, execute the `AI Toolkit: Run fine-tuning` command.

The job streaming log will be displayed in the output panel if the job has started running. 
> **Note:** The job might be queued if there are insufficient resources available. If the log fails to display when the job starts, you can wait for a while and then execute the `AI Toolkit: Show the running fine-tuning job streaming logs` command to re-connect to the streaming log.
    
During this process, QLoRA will be used for fine-tuning, and will create LoRA adapters for the model to use during inference.
The results of the fine-tuning will be stored in the Azure Files.

### Provision Inference Endpoint
After the adapters are trained in the remote environment, you can use a simple Gradio application to interact with the model.  
Similar to the fine-tuning process, you need to set up the Azure Resources for remote inference by executing the `AI Toolkit: Provision Azure Container Apps for inference.` from the command palette. 
   
By default, the subscription and the resource group for inference should match those used for fine-tuning. The inference will use the same Azure Container App Environment and access the model and model adapter stored in Azure Files, which were generated during the fine-tuning step. 

Once provisioning is successfully completed, you can find the web API endpoint under `ACA_APP_ENDPOINT` within `./infra/inference.config.json`. You are now ready to evaluate the model using this endpoint.

### Modifying the Inference Code  
If you wish to revise the inference code, please execute the `AI Toolkit: Update code for inference` command. This will synchronize your latest code with ACA and restart the replica.  

### Advanced usage
For more information on remote development with AI Toolkit, refer to the [Fine-Tuning models remotely](https://aka.ms/ai-toolkit/remote-provision) and [Inferencing with the fine-tuned model](https://aka.ms/ai-toolkit/remote-inference) documentation.