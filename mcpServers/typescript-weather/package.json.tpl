{
  "name": "{{SafeProjectNameLowerCase}}",
  "version": "0.0.1",
  "description": "My MCP Server",
  "main": "./lib/src/index.js",
  "scripts": {
    "dev:http": "nodemon --exec node --inspect=9239 --signal SIGINT -r ts-node/register ./src/index.ts http",
    "dev:stdio": "nodemon --quiet --exec node --signal SIGINT -r ts-node/register ./src/index.ts stdio",
    "dev:inspector:http": "mcp-inspector --config .inspector.json --server {{SafeProjectNameLowerCase}}_http",
    "dev:inspector:stdio": "mcp-inspector --config .inspector.json --server {{SafeProjectNameLowerCase}}_stdio",
    "build": "tsc --build",
    "start:http": "node ./lib/src/index.js http",
    "start:stdio": "node ./lib/src/index.js stdio"
},
  "author": "",
  "license": "ISC",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.20.1",
    "express": "^4.21.2",
    "zod": "^3.24.2"
  },
  "devDependencies": {
    "@modelcontextprotocol/inspector": "0.17.2",
    "@types/express": "^5.0.0",
    "@types/node": "^22.13.10",
    "nodemon": "^3.1.9",
    "ts-node": "^10.9.2",
    "typescript": "^5.8.2"
  }
}
