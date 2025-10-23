
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { server } from "./server";

// Start the server
async function main() {
  const args = process.argv.slice(2);
  const type = args.at(0) || "stdio";
  if (type === "http") {
    const app = express();
    app.use(express.json());

    app.post('/mcp', async (req, res) => {
      // Create a new transport for each request to prevent request ID collisions
      const transport = new StreamableHTTPServerTransport({
          sessionIdGenerator: undefined,
          enableJsonResponse: true
      });

      res.on('close', () => {
          transport.close();
      });

      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    });

  const port = parseInt(process.env.PORT || '3001');
  app.listen(port, () => {
      console.log(`MCP Server running on http://localhost:${port}/mcp`);
  }).on('error', error => {
      console.error('Server error:', error);
      throw error;
  });
  } else if (type === "stdio") {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("MCP Server running on stdio");
  } else {
    throw new Error(`Unknown transport type: ${type}`);
  }
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});