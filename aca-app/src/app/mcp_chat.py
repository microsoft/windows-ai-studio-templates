import os
from typing import Optional
from contextlib import AsyncExitStack
import json

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import AssistantMessage, SystemMessage, ToolMessage, UserMessage
from azure.ai.inference.models import ImageContentItem, ImageUrl, TextContentItem
from azure.core.credentials import AzureKeyCredential

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPChat:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = ChatCompletionsClient(
            endpoint = "https://models.inference.ai.azure.com",
            credential = AzureKeyCredential(os.environ["TEST_GITHUB_TOKEN"]),
        )
        self.connected = False

    async def connect_to_server(self):
        if self.connected:
            return
        server_params = StdioServerParameters(
            command="node",
            args=[
                ".mcp/lib/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js",
                ".working"
            ],
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\n\nConnected to server with tools:", [tool.name for tool in tools])
        self.connected = True

    async def chatWithTools(self, text: str):
        await self.connect_to_server()
        messages = [
            UserMessage(content = [
                TextContentItem(text = text),
            ])
        ]
        output = ""

        listToolsRes = await self.session.list_tools()
        available_tools = [{ 
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in listToolsRes.tools]
        output = "\n\nConnected to server with tools:" + ", ".join([tool.name for tool in listToolsRes.tools])
        yield output

        while True:
            # Call model
            response = self.client.complete(
                messages = messages,
                model = "gpt-4o-mini",
                max_tokens = 2048,
                temperature = 0.8,
                top_p = 0.1,
                tools=available_tools,
                tool_choice="auto"
            )
            toolCalls = []

            if len(response.choices) > 0:
                choice = response.choices[0]
                if choice.message.tool_calls is not None and len(choice.message.tool_calls) > 0:
                    for tool_call in choice.message.tool_calls:
                        toolCalls.append({
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        })
                messages.append(choice.message)
                if choice.message.content is not None and len(choice.message.content) > 0:
                    output = "\n\n[Model]: " + f"{choice.message.content}"
                    yield output

            if (len(toolCalls) == 0):
                break
            else:
                for toolCall in toolCalls:
                    # Call the tool
                    output = "\n\n[Tool]> " + f"Calling tool: {toolCall['name']} ({toolCall['arguments'][:15]} ...)"
                    yield output
                    result = await self.session.call_tool(toolCall["name"], json.loads(toolCall["arguments"]))
                    output = "\n\n[Tool]> " + f"Tool result: {result.content[0].text}"
                    yield output
                    messages.append(ToolMessage(
                        content=result.content[0].text,
                        tool_call_id=toolCall["id"],
                    ))
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def ask(text: str):
    client = MCPChat()
    async for delta in client.chatWithTools(text):
        yield delta

app = FastAPI()

app.mount("/working", StaticFiles(directory=".working"), name="working")

@app.get("/chat")
def chat(request: Request):
    text = request.query_params.get("text", "")
    return StreamingResponse(ask(text), media_type='text/event-stream')

@app.get("/")
def root():
    return {"message": "Running on /chat"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)