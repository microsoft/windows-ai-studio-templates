# Simple Workflow Agent

This sample demonstrates a **sequential two-agent workflow** pattern using the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework):

```
User Input → Writer Agent → Reviewer Agent → Final Output
```

* **Writer Agent** - Receives the user's request and generates clear, engaging content
* **Reviewer Agent** - Reviews the writer's content and provides constructive feedback on clarity, completeness, and quality

## Prerequisites

- [Python 3.10 or higher](https://www.python.org/downloads/)
- [Python VS Code extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [AI Toolkit VS Code extension](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)
- [Microsoft Foundry Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.azure-ai-foundry) with [a default project configured and a deployed model](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/get-started-projects-vs-code)
- [Azure CLI installed](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) and [authenticated (for Azure credential authentication)](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

## Setup

### Option 1: Quick Setup with Copilot

Click [Setup Debug Environment](vscode://ms-windows-ai-studio.windows-ai-studio/setup_debug) to automatically configure your debug environment with GitHub Copilot.

### Option 2: Manual Setup

#### 1. Create a Python Virtual Environment

You can [create a virtual environment using the Python extension](https://code.visualstudio.com/docs/python/environments#_creating-environments) or by running the following command in the terminal:

```bash
python -m venv .venv
```

Then activate the virtual environment:

- **Windows**: `.venv\Scripts\activate`
- **macOS/Linux**: `source .venv/bin/activate`

#### 2. Install Dependencies

**Important**: The `--pre` flag is required while Agent Framework is in preview.

```bash
pip install -r requirements.txt --pre
```

#### 3. Configure Environment

Copy [.env.example](.env.example) to `.env` and update with your Foundry project details:

```env
FOUNDRY_PROJECT_ENDPOINT=<your-foundry-project-endpoint>
FOUNDRY_MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

## Running the Workflow

### Option 1: Press F5 (Recommended)

Press **F5** in VS Code to start debugging. This will:
1. Start the HTTP server with debugging enabled
2. Open the AI Toolkit Agent Inspector for interactive testing
3. Allow you to set breakpoints and inspect the workflow

### Option 2: Run in Terminal

Run as HTTP server (default):

```bash
python workflow.py
```

Or run in CLI mode for quick testing:

```bash
python workflow.py --cli
```

## Next Steps

- **Add Tracing** - Use AI Toolkit's trace viewer to monitor and troubleshoot runtime issues
- **Set Up Evaluation** - Create test datasets and define metrics to measure workflow quality
- **Deploy** - Use AI Toolkit to deploy your workflow to Microsoft Foundry
- **Explore Patterns** - Try conditional routing, parallel execution, human-in-the-loop, and tool integration

## Troubleshooting

### Port Already in Use

If you see port conflict errors:
- The default ports are 5679 (debugger) and 8087 (HTTP server)
- Stop any processes using these ports or update ports in [.vscode/tasks.json](.vscode/tasks.json)

### Authentication Errors

Ensure you're logged in to Azure:

```bash
az login
```

### Model Not Found

Verify your model deployment:
1. Open AI Toolkit Model Catalog
2. Check your deployed models in Microsoft Foundry
3. Ensure `.env` exists (copy from `.env.example`) and has the correct deployment name

## Learn More

- [Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [AI Toolkit Agent Test Tool](http://aka.ms/AIToolkit/doc/test-tool)

## Support

For issues or questions:
- Agent Framework: https://github.com/microsoft/agent-framework/issues
- AI Toolkit: https://github.com/microsoft/vscode-ai-tools/issues
