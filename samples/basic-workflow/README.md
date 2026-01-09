# Simple Workflow Agent: Writer → Reviewer

A production-ready workflow agent built with Microsoft Agent Framework SDK demonstrating sequential agent collaboration.

## Project Structure

```
basic-workflow/
├── workflow.py              # Main workflow implementation
├── .env.example             # Environment configuration template
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── .vscode/
    ├── launch.json         # Debug configurations
    └── tasks.json          # Build/run tasks
```

## Prerequisites

- Python 3.10 or higher
- VS Code with AI Toolkit extension installed
- Microsoft Foundry project with deployed model
- Azure authentication configured (`az login`)

## Setup

### Quick Setup with Copilot

Click [Setup Debug Environment](vscode://ms-windows-ai-studio.windows-ai-studio/setup_debug) to automatically configure your debug environment with GitHub Copilot.

### Manual Setup

#### 1. Install Dependencies

**Important**: The `--pre` flag is required while Agent Framework is in preview.

```bash
pip install -r requirements.txt --pre
```

#### 2. Configure Environment

Copy [.env.example](.env.example) to `.env` and update with your Foundry project details:

```env
FOUNDRY_PROJECT_ENDPOINT=<your-foundry-project-endpoint>
FOUNDRY_MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>
```

## Running the Workflow

### Option 1: Press F5 (Recommended)

Press **F5** in VS Code to start debugging. This will:
1. Start the HTTP server with debugging enabled
2. Open the AI Toolkit Test Tool for interactive testing
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
- [Microsoft Foundry](https://ai.azure.com)
- [AI Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-ai-tools)

## Support

For issues or questions:
- Agent Framework: https://github.com/microsoft/agent-framework/issues
- AI Toolkit: https://github.com/microsoft/vscode-ai-tools/issues
