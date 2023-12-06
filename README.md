# Windows AI Studio Preview

## Overview
[Windows AI Studio](https://aka.ms/AIforWindows) simplifies generative AI app development by bringing together cutting-edge AI development tools and models from Azure AI Studio Catalog and other catalogs like Hugging Face. You will be able browse the AI models catalog powered by Azure ML and Hugging Face for public models that you can download locally, fine- tune, test and use them in your Windows application.
As all of the computation happens locally, please make sure your device can handle the load.

## Quick Start

In this section you will learn how to quickly start with Windows AI Studio.

### Install Windows AI Studio Preview

Windows AI Studio is shipped as a [Visual Studio Code Extension](https://code.visualstudio.com/docs/setup/additional-components#_vs-code-extensions), so you need to install [VS Code](https://code.visualstudio.com/docs/setup/windows) first, and download Windows AI Studio from the [VS Marketplace](https://marketplace.visualstudio.com/VSCode).

### Available Actions

Upon launching Windows AI Studio, you can select from the following options:
- Start Model fine- tuning
- Start RAG Project
- Phi-2 Model Playground
- Windows Optimized Models


![Actions](/Images/studio_Actions.png)

### Start Model Fine- tuning

To initiate the local fine- tuning session using QLoRA, select a model you want to fine- tune from our catalog powered by AzureML.

> ***Note*** You do not need an Azure Account to download the models

Start by selecting a project name and location. Next, select a model from the model catalog. You will be prompted to download the project template. You can then click Configure Project to adjust various settings. 
We use [Olive](https://microsoft.github.io/Olive/overview/olive.html) to run QLoRA fine-tuning on a PyTorch model from our catalog. All of the settings are preset with the default values to optimize to run the fine- tuning process locally with optimized use of memory.

![Configure the model](/Images/fine- tune.jpg)

| Settings                       | Data Type | Default Value | Description |
| ----------------------------- | --------- | --------------| ----------- |
| Compute Dtype                 | Str       | bfloat16      | Data type for model weights and adapter weights. For 4bit quantized model, it is also the computation data type for the quantized modules. Should be one of bfloat16, float16 or float32 |
| Quant type                    |           | nf4           | Quantization data type to use. Should be one of fp4 or nf4 |
| Double quant                  | Bool      | yes           | Whether to use nested quantization where the quantization constants from the first quantization are quantized again |
| Lora r                        | Int       | 64            | Lora attention dimension |
| Lora alpha                    | Float     | 16            | The alpha parameter for Lora scaling |
| Lora dropout                  | Float     | 0.1           | The dropout probability for Lora layers |
| Eval dataset size             | Float     | 1024          | Size of the validation dataset |
| Seed                          | Int       | 0             | Random seed for initialization |
| Data Seed                     | Int       | 42            | Random seed to be used with data samplers |
| Per device train batch size   | Int       | 1             | The batch size per GPU for training |
| Per device eval batch size    | Int       | 1             | The batch size per GPU for evaluation |
| Gradient accumulation steps   | Int       | 4             | Number of updates steps to accumulate the gradients for, before performing a backward/update pass |
| Enable Gradient checkpoint    | Bool      | yes           | Use gradient checkpointing. Recommended to save the memory |
| Learning rate                 | Float     | 0.0002       |The initial learning rate for AdamW |
| Max steps                     | Int       | -1           |If set to a positive number, the total number of training steps to perform. Overrides num_train_epochs. In case of using a finite iterable dataset the training may stop before reaching the set number of steps when all data is exhausted|



After all the parameters are set, click **Generate Project**.
This will:
 - Initiate the model download
 - Install all prerequisites and dependencies
 - Create VS Code workspace

When the model is downloaded, you can launch the project from Windows AI Studio.


### Start RAG Project

**Coming soon!**

### Phi-2 Model Playground

**Coming soon!**

### Windows Optimized Models

This is the collection of publicly available AI models already optimized for Windows. The models are stored in the different locations including Hugging Face, GitHub and others, but you can browse the models and find all of them in one place ready for downloading and using in your Windows application.

### Q&A

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
