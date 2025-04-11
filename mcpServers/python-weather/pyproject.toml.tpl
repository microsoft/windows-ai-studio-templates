[project]
name = "{{SafeProjectNameLowerCase}}"
version = "0.1.0"
description = "A simple MCP weather server"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp==1.4.1"
]

[project.optional-dependencies]
dev = ["debugpy==1.8.8"]