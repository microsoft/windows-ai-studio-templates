# Windows AI Studio Preview

## Overview
[Windows AI Studio](add link to Studio) simplifies generative AI app development by bringing together cutting-edge AI development tools and models from Azure AI Studio Catalog and other catalogs like Hugging Face. You will be able browse the AI models catalog powered by Azure ML and Hugging Face for public models that you can download locally, fine- tune, test and add them to your Windows application.
[Windows AI Studio](add link to Studio)

## Quick Start

In this section you will learn how to quickly start with Windows AI Studio

### Install Windows AI Studio Preview

Windows AI Studio is shipped as [Visual Studio Code Extension](https://code.visualstudio.com/docs/setup/additional-components#_vs-code-extensions), so you need to install [VS Code](https://code.visualstudio.com/docs/setup/windows) first and dowload the Windows AI Studio from the [VS Marketplace](https://marketplace.visualstudio.com/VSCode).

### Available Actions

Upon lanching Windows AI Studio, there are several actions you can do:
- Start Model Finetuning
- Start Dataset Generation

![Actions](/Images/studio_Actions.png)

### Start Model Finetuning

To initiate the local finetuning session using QLoRA, select a model you want to finetune from our catalog powered by AzureML.

> ***Note*** You do not need Azure Account to download the models

Once, a model is selected it is time to configure the project. You will be promp to download the project template. But first, you can set configuration settings via UI.

![Configure the model](/Images/fineTune.jpg)

After all the parameters are set, click **Generate Progect**.
That will:
 - Initiate the model download
 - Install all prerequisites and dependencies
 - Create VS Code workspace

When the model is downloaded, you can launch you project
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
