"""Simple Workflow Agent: Writer → Reviewer

This workflow demonstrates a sequential two-agent pattern:
- Writer agent creates content based on user input
- Reviewer agent reviews and provides feedback on the content

The workflow can run in HTTP server mode for debugging and deployment.
"""

import asyncio
import os
from uuid import uuid4

from agent_framework import (
    AgentRunResponseUpdate,
    AgentRunUpdateEvent,
    ChatAgent,
    ChatMessage,
    Executor,
    Role,
    TextContent,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Foundry Configuration
ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT_NAME = os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME", "")

# Validate required environment variables
if not ENDPOINT or not MODEL_DEPLOYMENT_NAME:
    missing_vars = []
    if not ENDPOINT:
        missing_vars.append("FOUNDRY_PROJECT_ENDPOINT")
    if not MODEL_DEPLOYMENT_NAME:
        missing_vars.append("FOUNDRY_MODEL_DEPLOYMENT_NAME")
    missing_str = ", ".join(missing_vars)
    raise RuntimeError(
        f"Missing required environment variable(s): {missing_str}. "
        "Please set them in your .env file or environment before running this workflow."
    )


class WriterExecutor(Executor):
    """Writer executor that generates content based on user input."""

    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id: str = "writer"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Generate content and forward the conversation to reviewer."""
        # Run the writer agent
        response = await self.agent.run(messages)
        
        # Add agent output as event for HTTP server response
        for message in response.messages:
            if message.role == Role.ASSISTANT and message.contents:
                await ctx.add_event(
                    AgentRunUpdateEvent(
                        self.id,
                        data=AgentRunResponseUpdate(
                            contents=[TextContent(text=f"Writer: {message.contents[-1].text}")],
                            role=Role.ASSISTANT,
                            response_id=str(uuid4()),
                        ),
                    )
                )
        
        # Extend conversation with writer's messages
        messages.extend(response.messages)
        
        # Forward to next agent in workflow
        await ctx.send_message(messages)


class ReviewerExecutor(Executor):
    """Reviewer executor that reviews content and provides feedback."""

    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id: str = "reviewer"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Review the content and yield final output."""
        # Run the reviewer agent
        response = await self.agent.run(messages)
        
        # Add agent output as event for HTTP server response
        for message in response.messages:
            if message.role == Role.ASSISTANT and message.contents:
                await ctx.add_event(
                    AgentRunUpdateEvent(
                        self.id,
                        data=AgentRunResponseUpdate(
                            contents=[TextContent(text=f"Reviewer: {message.contents[-1].text}")],
                            role=Role.ASSISTANT,
                            response_id=str(uuid4()),
                        ),
                    )
                )
        
        # Yield the final output
        await ctx.yield_output(response.text)


async def main():
    """Main entry point - runs the workflow as HTTP server or CLI."""
    import sys
    
    # Keep async context managers alive for the entire workflow execution
    async with DefaultAzureCredential() as credential:
        async with AzureAIClient(
            project_endpoint=ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT_NAME,
            credential=credential,
        ).create_agent(
            name="Writer",
            instructions=(
                "You are an excellent content writer. "
                "Create clear, engaging content based on the user's request. "
                "Focus on clarity, accuracy, and proper structure."
            ),
        ) as writer_agent, AzureAIClient(
            project_endpoint=ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT_NAME,
            credential=credential,
        ).create_agent(
            name="Reviewer",
            instructions=(
                "You are an expert content reviewer. "
                "Review the writer's content and provide constructive feedback. "
                "Focus on clarity, completeness, accuracy, and overall quality."
            ),
        ) as reviewer_agent:
            # Build the workflow: Writer → Reviewer
            workflow = (
                WorkflowBuilder()
                .register_executor(lambda: WriterExecutor(writer_agent), name="writer")
                .register_executor(lambda: ReviewerExecutor(reviewer_agent), name="reviewer")
                .add_edge("writer", "reviewer")
                .set_start_executor("writer")
                .build()
            )
            
            # Convert workflow to agent for HTTP server mode
            agent = workflow.as_agent(name="WriterReviewerWorkflow")
            
            # Check if running in CLI mode (default is server mode)
            if "--cli" in sys.argv:
                # CLI mode for testing
                print("Running workflow agent in CLI mode...")
                
                # Test with a sample query
                user_message = "Write a short blog post about the benefits of AI agents in software development."
                print(f"\nUser: {user_message}\n")
                
                response = await agent.run([ChatMessage(role=Role.USER, text=user_message)])
                
                print("\n=== Workflow Completed ===")
                for msg in response.messages:
                    if msg.role == Role.ASSISTANT:
                        author = msg.author_name or "Assistant"
                        print(f"\n{author}:")
                        print(msg.text)
            else:
                # Server mode (default)
                print("Starting workflow agent HTTP server...")
                from azure.ai.agentserver.agentframework import from_agent_framework
                
                await from_agent_framework(agent).run_async()


if __name__ == "__main__":
    asyncio.run(main())
