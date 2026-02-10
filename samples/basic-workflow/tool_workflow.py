"""Tool Workflow Sample: Researcher (with tools) → Summarizer (Deterministic)

This workflow demonstrates an agent that uses **tools** (function calling)
within the standard Agent Framework APIs, but backed entirely by
deterministic logic – no AI models, credentials, or network access required.

Key concepts exercised:
- ``ai_function`` decorator to define tools
- ``FunctionCallContent`` / ``FunctionResultContent`` in ChatMessage to
  represent the tool-call round-trip
- ``DeterministicToolAgent`` – a BaseAgent subclass whose ``run()`` detects
  which tool to call, invokes it, and returns the result as a proper
  ``AgentRunResponse`` (mirroring what a real ChatAgent + model would do)
- Standard ``Executor`` / ``WorkflowBuilder`` / ``WorkflowContext`` plumbing
  identical to a real workflow

Flow:
    User query → **ResearcherExecutor** (agent picks & calls tools) →
    **SummarizerExecutor** (agent summarises the collected facts) →
    final output
"""

import asyncio
import json
from typing import Annotated, Any, Callable
from uuid import uuid4

from agent_framework import (
    AgentRunResponse,
    AgentRunResponseUpdate,
    AgentRunUpdateEvent,
    AgentThread,
    BaseAgent,
    ChatMessage,
    Executor,
    FunctionCallContent,
    FunctionResultContent,
    Role,
    TextContent,
    WorkflowBuilder,
    WorkflowContext,
    ai_function,
    handler,
)


# ---------------------------------------------------------------------------
# Tools – decorated with @ai_function just like a real project
# ---------------------------------------------------------------------------

@ai_function
def get_population(country: Annotated[str, "Name of the country"]) -> str:
    """Look up the population of a country."""
    # Deterministic lookup table
    data = {
        "united states": "331 million",
        "china": "1.4 billion",
        "india": "1.4 billion",
        "brazil": "214 million",
        "germany": "84 million",
        "japan": "125 million",
    }
    return data.get(country.lower(), f"Population data not found for '{country}'")


@ai_function
def get_capital(country: Annotated[str, "Name of the country"]) -> str:
    """Look up the capital city of a country."""
    data = {
        "united states": "Washington, D.C.",
        "china": "Beijing",
        "india": "New Delhi",
        "brazil": "Brasília",
        "germany": "Berlin",
        "japan": "Tokyo",
    }
    return data.get(country.lower(), f"Capital data not found for '{country}'")


@ai_function
def get_language(country: Annotated[str, "Name of the country"]) -> str:
    """Look up the primary language spoken in a country."""
    data = {
        "united states": "English",
        "china": "Mandarin Chinese",
        "india": "Hindi (and English)",
        "brazil": "Portuguese",
        "germany": "German",
        "japan": "Japanese",
    }
    return data.get(country.lower(), f"Language data not found for '{country}'")


# Collect all tools in a list for easy reference
ALL_TOOLS = [get_population, get_capital, get_language]
TOOL_MAP = {t.name: t for t in ALL_TOOLS}


# ---------------------------------------------------------------------------
# DeterministicToolAgent – simulates a ChatAgent that performs tool calls
# ---------------------------------------------------------------------------

class DeterministicToolAgent(BaseAgent):
    """A mock agent that deterministically decides which tools to call.

    Instead of asking a model, it applies a simple heuristic to pick tools
    based on keywords in the user's message, calls them, and returns a
    response containing the full tool-call round-trip (FunctionCallContent →
    FunctionResultContent → final TextContent).
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        instructions: str | None = None,
        tools: list[Any] | None = None,
        tool_picker: Callable[[str, dict[str, Any]], list[tuple[str, dict[str, Any]]]] | None = None,
        response_builder: Callable[[list[tuple[str, str]]], str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            name: Agent name.
            instructions: System prompt (kept for parity with ChatAgent).
            tools: List of ai_function-decorated tools the agent can use.
            tool_picker: ``(user_text, tool_map) -> [(tool_name, {arg: val})]``
                         Deterministic function that decides which tools to call.
            response_builder: ``([(tool_name, result_str)]) -> final_text``
                              Builds the agent's final text from tool results.
        """
        super().__init__(name=name, **kwargs)
        self.instructions = instructions
        self._tools = {t.name: t for t in (tools or [])}
        self._tool_picker = tool_picker or self._default_tool_picker
        self._response_builder = response_builder or self._default_response_builder

    # -- AgentProtocol ---------------------------------------------------------

    async def run(
        self,
        messages: str | ChatMessage | list[str] | list[ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs: Any,
    ) -> AgentRunResponse:
        normalized = self._normalize_messages(messages)

        # Extract latest user text
        user_text = ""
        for msg in reversed(normalized):
            if msg.role == Role.USER:
                user_text = msg.text or ""
                break

        # 1. Decide which tools to call (deterministic heuristic)
        calls = self._tool_picker(user_text, self._tools)

        response_messages: list[ChatMessage] = []
        tool_results: list[tuple[str, str]] = []

        for tool_name, tool_args in calls:
            call_id = f"call_{uuid4().hex[:8]}"

            # -- assistant message with FunctionCallContent (model "requests" a tool call)
            response_messages.append(
                ChatMessage(
                    role=Role.ASSISTANT,
                    contents=[
                        FunctionCallContent(
                            call_id=call_id,
                            name=tool_name,
                            arguments=tool_args,
                        )
                    ],
                    author_name=self.name,
                )
            )

            # -- invoke the tool
            tool_fn = self._tools[tool_name]
            result = tool_fn(**tool_args)
            if asyncio.iscoroutine(result):
                result = await result
            result_str = str(result)
            tool_results.append((tool_name, result_str))

            # -- tool message with FunctionResultContent
            response_messages.append(
                ChatMessage(
                    role=Role.TOOL,
                    contents=[
                        FunctionResultContent(
                            call_id=call_id,
                            result=result_str,
                        )
                    ],
                )
            )

        # 2. Build the final assistant reply that incorporates tool results
        final_text = self._response_builder(tool_results)
        response_messages.append(
            ChatMessage(
                role=Role.ASSISTANT,
                contents=[TextContent(text=final_text)],
                author_name=self.name,
            )
        )

        return AgentRunResponse(messages=response_messages, response_id=str(uuid4()))

    async def run_stream(self, messages=None, *, thread=None, **kwargs):  # type: ignore[override]
        response = await self.run(messages, thread=thread, **kwargs)
        for msg in response.messages:
            for content in msg.contents:
                yield AgentRunResponseUpdate(
                    contents=[content],
                    role=msg.role,
                    response_id=response.response_id,
                )

    # -- Default helpers -------------------------------------------------------

    @staticmethod
    def _default_tool_picker(
        user_text: str, tool_map: dict[str, Any]
    ) -> list[tuple[str, dict[str, Any]]]:
        """Keyword-based heuristic: pick tools whose name partially appears in the query."""
        text_lower = user_text.lower()
        calls: list[tuple[str, dict[str, Any]]] = []

        # Try to extract a country name from the query
        known_countries = [
            "United States", "China", "India", "Brazil", "Germany", "Japan",
        ]
        country = "United States"  # fallback
        for c in known_countries:
            if c.lower() in text_lower:
                country = c
                break

        keyword_map: dict[str, str] = {
            "population": "get_population",
            "capital": "get_capital",
            "language": "get_language",
        }
        matched = False
        for keyword, tool_name in keyword_map.items():
            if keyword in text_lower and tool_name in tool_map:
                calls.append((tool_name, {"country": country}))
                matched = True

        # If no keyword matched, call all available tools
        if not matched:
            for tool_name in tool_map:
                calls.append((tool_name, {"country": country}))

        return calls

    @staticmethod
    def _default_response_builder(tool_results: list[tuple[str, str]]) -> str:
        """Combine tool results into a readable summary."""
        if not tool_results:
            return "No tools were called."
        lines = ["Here are the research findings:"]
        for tool_name, result in tool_results:
            lines.append(f"  - {tool_name}: {result}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deterministic summarizer (no tools, just text processing)
# ---------------------------------------------------------------------------

class DeterministicSummarizerAgent(BaseAgent):
    """A mock agent that deterministically summarises the conversation."""

    def __init__(self, *, name: str | None = None, instructions: str | None = None, **kwargs: Any):
        super().__init__(name=name, **kwargs)
        self.instructions = instructions

    async def run(
        self,
        messages: str | ChatMessage | list[str] | list[ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs: Any,
    ) -> AgentRunResponse:
        normalized = self._normalize_messages(messages)

        # Collect all FunctionResultContent values from the conversation
        facts: list[str] = []
        for msg in normalized:
            for content in msg.contents:
                if isinstance(content, FunctionResultContent):
                    facts.append(str(content.result))

        if facts:
            summary = (
                "Summary of research:\n"
                + "\n".join(f"  • {fact}" for fact in facts)
                + f"\n\nTotal facts gathered: {len(facts)}."
            )
        else:
            # Fallback: just echo back the last assistant message
            last_text = ""
            for msg in reversed(normalized):
                if msg.role == Role.ASSISTANT and msg.text:
                    last_text = msg.text
                    break
            summary = f"Summary: {last_text}" if last_text else "Nothing to summarise."

        response_msg = ChatMessage(
            role=Role.ASSISTANT,
            contents=[TextContent(text=summary)],
            author_name=self.name,
        )
        return AgentRunResponse(messages=[response_msg], response_id=str(uuid4()))

    async def run_stream(self, messages=None, *, thread=None, **kwargs):  # type: ignore[override]
        response = await self.run(messages, thread=thread, **kwargs)
        for msg in response.messages:
            for content in msg.contents:
                yield AgentRunResponseUpdate(
                    contents=[content],
                    role=msg.role,
                    response_id=response.response_id,
                )


# ---------------------------------------------------------------------------
# Workflow executors
# ---------------------------------------------------------------------------

class ResearcherExecutor(Executor):
    """Executor that runs the researcher agent (which uses tools)."""

    agent: BaseAgent

    def __init__(self, agent: BaseAgent, id: str = "researcher"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        response = await self.agent.run(messages)

        # Emit events for every assistant message
        for message in response.messages:
            if message.role == Role.ASSISTANT and message.contents:
                # Show tool calls and text; skip pure tool-result messages
                display_parts: list[str] = []
                for content in message.contents:
                    if isinstance(content, FunctionCallContent):
                        args_str = json.dumps(content.arguments) if isinstance(content.arguments, dict) else str(content.arguments)
                        display_parts.append(f"[tool call] {content.name}({args_str})")
                    elif isinstance(content, TextContent):
                        display_parts.append(content.text)
                if display_parts:
                    await ctx.add_event(
                        AgentRunUpdateEvent(
                            self.id,
                            data=AgentRunResponseUpdate(
                                contents=[TextContent(text=f"Researcher: {' | '.join(display_parts)}")],
                                role=Role.ASSISTANT,
                                response_id=str(uuid4()),
                            ),
                        )
                    )

        # Extend conversation & forward
        messages.extend(response.messages)
        await ctx.send_message(messages)


class SummarizerExecutor(Executor):
    """Executor that runs the summarizer agent."""

    agent: BaseAgent

    def __init__(self, agent: BaseAgent, id: str = "summarizer"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        response = await self.agent.run(messages)

        for message in response.messages:
            if message.role == Role.ASSISTANT and message.contents:
                await ctx.add_event(
                    AgentRunUpdateEvent(
                        self.id,
                        data=AgentRunResponseUpdate(
                            contents=[TextContent(text=f"Summarizer: {message.contents[-1].text}")],
                            role=Role.ASSISTANT,
                            response_id=str(uuid4()),
                        ),
                    )
                )

        await ctx.yield_output(response.text)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main():
    """Main entry point – runs the tool workflow as HTTP server or CLI."""
    import sys

    # --- Agents ---------------------------------------------------------------
    researcher_agent = DeterministicToolAgent(
        name="researcher",
        instructions=(
            "You are a research assistant. Use your tools to look up facts "
            "about countries, then present the results clearly."
        ),
        tools=ALL_TOOLS,
    )

    summarizer_agent = DeterministicSummarizerAgent(
        name="summarizer",
        instructions=(
            "You are a summariser. Condense the researcher's findings into "
            "a concise brief."
        ),
    )

    # --- Workflow: Researcher → Summarizer ------------------------------------
    workflow = (
        WorkflowBuilder()
        .register_executor(lambda: ResearcherExecutor(researcher_agent), name="researcher")
        .register_executor(lambda: SummarizerExecutor(summarizer_agent), name="summarizer")
        .add_edge("researcher", "summarizer")
        .set_start_executor("researcher")
        .build()
    )

    agent = workflow.as_agent(name="ToolWorkflow")

    if "--cli" in sys.argv:
        print("Running tool workflow in CLI mode (deterministic, no AI)...\n")

        user_message = "Tell me about Japan – population, capital, and language."
        print(f"User: {user_message}\n")

        response = await agent.run([ChatMessage(role=Role.USER, text=user_message)])

        print("\n=== Workflow Completed ===")
        for msg in response.messages:
            if msg.role == Role.ASSISTANT:
                author = msg.author_name or "Assistant"
                print(f"\n{author}:")
                print(msg.text)
    else:
        print("Starting tool workflow HTTP server (deterministic, no AI)...")
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
