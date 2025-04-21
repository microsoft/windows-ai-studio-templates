# Weather MCP Server

This is a sample MCP Server in TypeScript implementing weather tools with mock responses. It can be used as a scaffold for your own MCP Server. It includes the following features: 

- **Weather Tool**: A tool that provides mocked weather information based on the given location.
- **Connect to Agent Builder**: A feature that allows you to connect the MCP server to the Agent Builder for testing and debugging.
- **Debug SSE in MCP Inspector**: A feature that allows you to debug the MCP Server using the MCP Inspector.
- **Debug STDIO in MCP Inspector**: A feature that allows you to debug the MCP Server using the MCP Inspector.

## Get started with the Weather MCP Server template

> **Prerequisites**
>
> To run the MCP Server in your local dev machine, you will need: [Node.js](https://nodejs.org/)

1. Open VS Code Debug panel. Select `Debug in Agent Builder` or press `F5` to start debugging the MCP server.
2. Use AI Toolkit Agent Builder to test the server with [this prompt](vscode://ms-windows-ai-studio.windows-ai-studio/open_prompt_builder?model_id=github/gpt-4o-mini&&system_prompt=You%20are%20a%20weather%20forecast%20professional%20that%20can%20tell%20weather%20information%20based%20on%20given%20location&&user_prompt=What%20is%20the%20weather%20in%20Shanghai?&track_from=vsc_md&mcp={{SafeProjectNameLowerCase}}). Server will be auto-connected to the Agent Builder.
3. Click `Run` to test the server with the prompt.

**Congratulations**! You have successfully run the Weather MCP Server in your local dev machine via Agent Builder as the MCP Client.
![DebugMCP](https://raw.githubusercontent.com/microsoft/windows-ai-studio-templates/refs/heads/dev/mcpServers/MCPScaffold.gif)

## What's included in the template
| Folder / File| Contents                                     |
| ------------ | -------------------------------------------- |
| `.vscode`    | VSCode files for debugging                   |
| `.aitk`      | Configurations for AI Toolkit                |
| `src`        | The source code for the weather mcp server   |

## How to debug the Weather MCP Server

> Notes:
> - [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a visual developer tool for testing and debugging MCP servers.
> - All debugging modes support breakpoints, so you can add breakpoints to the tool implementation code.

| Debug Mode | Description | Steps to debug |
| ---------- | ----------- | --------------- |
| Agent Builder | Debug the MCP server in the Agent Builder via AI Toolkit. | 1. Open VS Code Debug panel. Select `Debug in Agent Builder` and press `F5` to start debugging the MCP server.<br>2. Use AI Toolkit Agent Builder to test the server with [this prompt](vscode://ms-windows-ai-studio.windows-ai-studio/open_prompt_builder?model_id=github/gpt-4o-mini&&system_prompt=You%20are%20a%20weather%20forecast%20professional%20that%20can%20tell%20weather%20information%20based%20on%20given%20location&&user_prompt=What%20is%20the%20weather%20in%20Shanghai?&track_from=vsc_md&mcp={{SafeProjectNameLowerCase}}). Server will be auto-connected to the Agent Builder.<br>3. Click `Run` to test the server with the prompt. |
| MCP Inspector for SSE | Debug the MCP server using the MCP Inspector. | 1. Open VS Code Debug panel. Select `Debug SSE in Inspector (Edge)` or `Debug SSE in Inspector (Chrome)`. Press F5 to start debugging.<br>2. When MCP Inspector launches in the browser, click the `Connect` button to connect this MCP server.<br>3. Then you can `List Tools`, select a tool, input parameters, and `Run Tool` to debug your server code.<br> |
| MCP Inspector for STDIO | Debug the MCP server using the MCP Inspector. | 1. Open VS Code Debug panel. Select `Debug STDIO in Inspector`. Press F5 to start debugging.<br>2. When MCP Inspector launches in your default browser, click the `Connect` button to connect this MCP server.<br>3. Then you can `List Tools`, select a tool, input parameters, and `Run Tool` to debug your server code.<br>4. Of course, you can add breakpoint to the tool implementation code. |

## Default Ports and customizations

| Debug Mode | Ports | Definitions | Customizations | Note |
| ---------- | ----- | ------------ | -------------- |-------------- |
| Agent Builder | 3001 | [tasks.json](.vscode/tasks.json) | Edit [launch.json](.vscode/launch.json), [tasks.json](.vscode/tasks.json), [index.ts](src/index.ts), [mcp.json](.aitk/mcp.json) to change ports and parameters. | N/A |
| MCP Inspector for SSE | 3001 (Server); 5173 and 3000 (Inspector) | [tasks.json](.vscode/tasks.json) | Edit [launch.json](.vscode/launch.json), [tasks.json](.vscode/tasks.json), [index.ts](src/index.ts), [mcp.json](.aitk/mcp.json) to change above ports.| N/A |
| MCP Inspector for STDIO | N/A | [launch.json](.vscode/launch.json) | N/A |   When launching debugging, it launches MCP Inspector with MCP settings pre-configured (default to `npm --silent run dev:stdio`). After clicking `Connect`, Inspector launches MCP server on STDIO, which is also auto-attached for debugging via VSCode. | 

## Feedback

If you have any feedback or suggestions for this template, please open an issue on the [AI Toolkit GitHub repository](https://github.com/microsoft/vscode-ai-toolkit/issues)