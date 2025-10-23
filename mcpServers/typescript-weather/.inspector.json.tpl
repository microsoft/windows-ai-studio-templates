{
  "mcpServers": {
    "{{SafeProjectNameLowerCase}}_stdio": {
      "type": "stdio",
      "command": "npm",
      "args": ["--silent", "run", "dev:stdio"]
    },
    "{{SafeProjectNameLowerCase}}_http": {
      "type": "streamable-http",
      "url": "http://localhost:3001/mcp"
    }
  }
}