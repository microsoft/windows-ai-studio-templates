# Basic LangGraph ReAct Agent

This sample demonstrates a **ReAct (Reasoning + Acting) agent** built with [LangGraph](https://github.com/langchain-ai/langgraph) and hosted via the [Azure AI Agent Server](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-langgraph):

```
User Input → ReAct Agent (reason → act → observe → repeat) → Final Output
```

* **get_word_length** – Returns the length of a word
* **calculator** – Evaluates a mathematical expression

## Prerequisites

- [Python 3.10 or higher](https://www.python.org/downloads/)
- [Python VS Code extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [AI Toolkit VS Code extension](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)
- An Azure OpenAI resource with a deployed chat model (e.g. `gpt-4o`)

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

```bash
pip install -r requirements.txt --pre
```

#### 3. Configure Environment

Copy [.env.example](.env.example) to `.env` and update with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.openai.azure.com/
OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<your-deployment-name>
```

## Running the Agent

### Option 1: Press F5 (Recommended)

Press **F5** in VS Code to start debugging. This will:
1. Start the HTTP server with debugging enabled
2. Open the AI Toolkit Agent Inspector for interactive testing
3. Allow you to set breakpoints and inspect the agent

### Option 2: Run in Terminal

```bash
python main.py
```

## Next Steps

- **Add Tools** – Extend the agent by adding more tools in `main.py`
- **Add Tracing** – Use AI Toolkit's trace viewer to monitor and troubleshoot runtime issues
- **Set Up Evaluation** – Create test datasets and define metrics to measure agent quality
- **Deploy** – Use AI Toolkit to deploy your agent to Microsoft Foundry

## Troubleshooting

### Port Already in Use

If you see port conflict errors:
- The default ports are 5679 (debugger) and 8087 (HTTP server)
- Stop any processes using these ports or update ports in [.vscode/tasks.json](.vscode/tasks.json)

### Authentication Errors

Ensure your `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` are correct in the `.env` file.

### Model Not Found

Verify your model deployment:
1. Check your deployed models in the Azure portal
2. Ensure `.env` exists (copy from `.env.example`) and has the correct `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`

## Learn More

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Azure AI Agent Server](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-langgraph)
- [AI Toolkit Agent Test Tool](http://aka.ms/AIToolkit/doc/test-tool)

## Support

For issues or questions:
- LangGraph: https://github.com/langchain-ai/langgraph/issues
- AI Toolkit: https://github.com/microsoft/vscode-ai-tools/issues
