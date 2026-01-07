# Workflows Getting Started Samples

## Installation

Microsoft Agent Framework Workflows support ships with the core `agent-framework` or `agent-framework-core` package, so no extra installation step is required.

To install with visualization support:

```bash
pip install agent-framework[viz] --pre
```

To export visualization images you also need to [install GraphViz](https://graphviz.org/download/).

## Samples Overview

### agents

| Sample | File | Concepts |
|---|---|---|
| Azure AI Agents (Streaming) | [agents/azure_ai_agents_streaming.py](./agents/azure_ai_agents_streaming.py) | Add Azure AI agents as edges and handle streaming events |
