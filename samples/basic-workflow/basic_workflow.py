"""Simple Workflow Sample: Writer → Reviewer (Deterministic)

This workflow demonstrates a sequential two-agent pattern using the same
ChatAgent / Executor APIs as a real AI workflow, but backed by deterministic
logic so it can run without models, credentials, or network access.

- DeterministicChatAgent  – a BaseAgent subclass whose ``run()`` returns
  canned content instead of calling a model.
- WriterExecutor / ReviewerExecutor – identical in structure to real
  executor code: they call ``self.agent.run(messages)`` and inspect the
  ``AgentRunResponse`` that comes back.

The workflow can run in HTTP server mode for debugging and deployment.
"""

import asyncio
from typing import Any, Callable
from uuid import uuid4

from agent_framework import (
    AgentRunResponse,
    AgentRunResponseUpdate,
    AgentRunUpdateEvent,
    AgentThread,
    BaseAgent,
    ChatAgent,
    ChatMessage,
    Executor,
    Role,
    TextContent,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)


# ---------------------------------------------------------------------------
# DeterministicChatAgent – drop-in replacement for ChatAgent
# ---------------------------------------------------------------------------

class DeterministicChatAgent(BaseAgent):
    """A mock ChatAgent that uses a deterministic function instead of a model.

    It implements the same ``run()`` contract as ChatAgent so that executors
    can treat it identically.
    """

    def __init__(
        self,
        *,
        logic: Callable[[list[ChatMessage]], str],
        name: str | None = None,
        instructions: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            logic: A callable that receives the message list and returns the
                   response text (deterministic).
            name: Agent name – forwarded to BaseAgent.
            instructions: Kept for parity with ChatAgent; not used by the logic.
        """
        super().__init__(name=name, **kwargs)
        self._logic = logic
        self.instructions = instructions

    # -- AgentProtocol methods --------------------------------------------------

    async def run(
        self,
        messages: str | ChatMessage | list[str] | list[ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs: Any,
    ) -> AgentRunResponse:
        normalized = self._normalize_messages(messages)
        text = self._logic(normalized)
        response_msg = ChatMessage(
            role=Role.ASSISTANT,
            contents=[TextContent(text=text)],
            author_name=self.name,
        )
        return AgentRunResponse(messages=[response_msg], response_id=str(uuid4()))

    async def run_stream(self, messages=None, *, thread=None, **kwargs):  # type: ignore[override]
        # Streaming not needed for this sample; delegate to run().
        response = await self.run(messages, thread=thread, **kwargs)
        for msg in response.messages:
            for content in msg.contents:
                yield AgentRunResponseUpdate(
                    contents=[content],
                    role=msg.role,
                    response_id=response.response_id,
                )


# ---------------------------------------------------------------------------
# Deterministic logic functions
# ---------------------------------------------------------------------------

def writer_logic(messages: list[ChatMessage]) -> str:
    """Deterministic writer: produces canned content from the user's request."""
    user_text = ""
    for msg in reversed(messages):
        if msg.role == Role.USER:
            user_text = msg.text or ""
            break
    word_count = len(user_text.split())
    return (
        f"Topic received: \"{user_text}\"\n"
        f"Word count of request: {word_count}\n\n"
        f"Here is a short article about the requested topic.\n"
        f"Paragraph 1: Introduction to the topic.\n"
        f"Paragraph 2: Key details and supporting points.\n"
        f"Paragraph 3: Conclusion and summary."
    )


def reviewer_logic(messages: list[ChatMessage]) -> str:
    """Deterministic reviewer: inspects conversation and returns a fixed review."""
    conversation_text = "\n".join(msg.text or "" for msg in messages)
    paragraph_count = conversation_text.count("Paragraph")
    return (
        f"Review of the writer's content:\n"
        f"- Paragraphs detected: {paragraph_count}\n"
        f"- Clarity: Good\n"
        f"- Completeness: Adequate\n"
        f"- Overall quality: Satisfactory\n"
        f"Recommendation: Approved with no changes needed."
    )


# ---------------------------------------------------------------------------
# Workflow executors – structurally identical to the real (AI-backed) version
# ---------------------------------------------------------------------------

class WriterExecutor(Executor):
    """Writer executor that generates content based on user input."""

    agent: BaseAgent

    def __init__(self, agent: BaseAgent, id: str = "writer"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Generate content and forward the conversation to reviewer."""
        # Run the agent (real or deterministic – same API)
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

        # Extend conversation with the agent's messages
        messages.extend(response.messages)

        # Forward to next agent in workflow
        await ctx.send_message(messages)


class ReviewerExecutor(Executor):
    """Reviewer executor that reviews content and provides feedback."""

    agent: BaseAgent

    def __init__(self, agent: BaseAgent, id: str = "reviewer"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Review the content and yield final output."""
        # Run the agent (real or deterministic – same API)
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


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main():
    """Main entry point – runs the workflow as HTTP server or CLI."""
    import sys

    # Create deterministic agents (swap these for real ChatAgent instances
    # when you're ready to use an actual model).
    writer_agent = DeterministicChatAgent(
        name="mywriter1",
        instructions=(
            "You are an excellent content writer. "
            "Create clear, engaging content based on the user's request. "
            "Focus on clarity, accuracy, and proper structure."
        ),
        logic=writer_logic,
    )

    reviewer_agent = DeterministicChatAgent(
        name="myreviewer1",
        instructions=(
            "You are an expert content reviewer. "
            "Review the writer's content and provide constructive feedback. "
            "Focus on clarity, completeness, accuracy, and overall quality."
        ),
        logic=reviewer_logic,
    )

    # Build the workflow: Writer → Reviewer
    workflow = (
        WorkflowBuilder()
        .register_executor(lambda: WriterExecutor(writer_agent), name="mywriter1")
        .register_executor(lambda: ReviewerExecutor(reviewer_agent), name="myreviewer1")
        .add_edge("mywriter1", "myreviewer1")
        .set_start_executor("mywriter1")
        .build()
    )

    # Convert workflow to agent for HTTP server mode
    agent = workflow.as_agent(name="WriterReviewerWorkflow")

    # Check if running in CLI mode (default is server mode)
    if "--cli" in sys.argv:
        # CLI mode for quick testing
        print("Running workflow in CLI mode (deterministic, no AI)...")

        user_message = "Write a short blog post about the benefits of automated testing."
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
        print("Starting workflow HTTP server (deterministic, no AI)...")
        from azure.ai.agentserver.agentframework import from_agent_framework
        from starlette.middleware.cors import CORSMiddleware

        server = from_agent_framework(agent)
        server.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
