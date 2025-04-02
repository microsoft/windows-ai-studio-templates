# MCP Server - Weather

This is a sample MCP Server in TypeScript implementing weather tools.

## Get Started

> **Prerequisites**
>
> To run the MCP Server in your local dev machine, you will need:
>
> - [Node.js](https://nodejs.org/)

First, before executing any code, install the dependencies.

- Open terminal and execute `npm install`

### Debug in MCP Inspector

- Open VSCode Debug panel. Select `Debug in Inspector (Edge)` or `Debug in Inspector (Chrome)`. Press F5 to start debugging.
- When MCP Inspector launches in the browser, click the `Connect` button to connect this MCP server.
- Then you can `List Tools`, select a tool, input parameters, and `Run Tool` to debug you server code.
- And ofcourse, you can add breakpoint to the tool implementation code.

<details>
  <summary>More Details</summary>

  When launching debugging, it runs two tasks

  - first, the MCP server is launched (by default on port 3001)
  - then, the MCP Inspector is launched (by default on port 5173 and 3000)

  The whole definition can be found in [tasks.json](.vscode/tasks.json). You can also edit [launch.json](.vscode/launch.json), [tasks.json](.vscode/tasks.json), [index.ts](src/index.ts) to change above ports.

</details>
