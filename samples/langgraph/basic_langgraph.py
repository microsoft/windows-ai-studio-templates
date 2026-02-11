"""Deterministic LangGraph Agent Sample: Country Research (with tools)

This demonstrates a LangGraph agent that uses **tools** (function calling)
backed entirely by deterministic logic – no AI models, credentials, or
network access required.

Uses the same country-research tools and data as tool_workflow.py so that
both frameworks produce identical results for the same input, enabling
controlled comparison experiments.

Key concepts exercised:
- LangGraph ``StateGraph`` with typed ``MessagesState``
- ``@tool`` decorated functions for country facts (population, capital, language)
- A deterministic "agent" node that picks tools via keyword heuristics
- A "tools" node that executes the selected tool calls
- Conditional routing between agent ↔ tools until done

Flow:
    User query → **agent** (picks tools by keywords) →
    **tools** (executes them) → **agent** (builds final answer) → done
"""

import uuid

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from starlette.middleware.cors import CORSMiddleware

from azure.ai.agentserver.langgraph import from_langgraph

load_dotenv()
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Tools – same deterministic lookup tables as tool_workflow.py
# ---------------------------------------------------------------------------

@tool
def get_population(country: str) -> str:
    """Look up the population of a country."""
    data = {
        "united states": "331 million",
        "china": "1.4 billion",
        "india": "1.4 billion",
        "brazil": "214 million",
        "germany": "84 million",
        "japan": "125 million",
    }
    return data.get(country.lower(), f"Population data not found for '{country}'")


@tool
def get_capital(country: str) -> str:
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


@tool
def get_language(country: str) -> str:
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


TOOLS = [get_population, get_capital, get_language]
TOOL_MAP = {t.name: t for t in TOOLS}

KNOWN_COUNTRIES = [
    "United States", "China", "India", "Brazil", "Germany", "Japan",
]


# ---------------------------------------------------------------------------
# Deterministic agent node – replaces the LLM with keyword heuristics
# ---------------------------------------------------------------------------

def _extract_tool_calls(user_text: str) -> list[dict]:
    """Keyword-based heuristic that decides which tools to call.

    Uses the same logic as DeterministicToolAgent._default_tool_picker in
    tool_workflow.py: match keywords → tool names, extract country from
    query, fall back to calling all tools if no keyword matched.
    """
    text_lower = user_text.lower()
    calls: list[dict] = []

    # Try to extract a country name from the query
    country = "United States"  # fallback
    for c in KNOWN_COUNTRIES:
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
        if keyword in text_lower and tool_name in TOOL_MAP:
            calls.append({
                "name": tool_name,
                "args": {"country": country},
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "tool_call",
            })
            matched = True

    # If no keyword matched, call all available tools (same as tool_workflow.py)
    if not matched:
        for tool_name in TOOL_MAP:
            calls.append({
                "name": tool_name,
                "args": {"country": country},
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "tool_call",
            })

    return calls


def agent_node(state: MessagesState) -> dict:
    """Deterministic agent node: either issues tool calls or produces a final answer."""
    messages = state["messages"]

    # Check if we already have tool results to summarise
    tool_results: list[tuple[str, str]] = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            tool_results.append((msg.name, msg.content))

    if tool_results:
        # We have results – build a final summary (mirrors tool_workflow.py output)
        lines = ["Here are the research findings:"]
        for name, result in tool_results:
            lines.append(f"  - {name}: {result}")
        return {"messages": [AIMessage(content="\n".join(lines))]}

    # No tool results yet – extract the user query and pick tools
    user_text = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_text = msg.content
            break

    tool_calls = _extract_tool_calls(user_text)

    if tool_calls:
        return {"messages": [AIMessage(content="", tool_calls=tool_calls)]}
    else:
        return {
            "messages": [
                AIMessage(content="No tools were called.")
            ]
        }


# ---------------------------------------------------------------------------
# Build the LangGraph
# ---------------------------------------------------------------------------

def should_continue(state: MessagesState) -> str:
    """Route to 'tools' if the last message has tool calls, otherwise END."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return END


def tools_node(state: MessagesState) -> dict:
    """Execute tool calls from the last AIMessage and return ToolMessages."""
    last = state["messages"][-1]
    results: list[ToolMessage] = []
    for tc in last.tool_calls:
        tool_fn = TOOL_MAP[tc["name"]]
        output = tool_fn.invoke(tc["args"])
        results.append(
            ToolMessage(content=str(output), name=tc["name"], tool_call_id=tc["id"])
        )
    return {"messages": results}


memory = MemorySaver()

graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

agent_executor = graph.compile(checkpointer=memory)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--cli" in sys.argv:
        print("Running deterministic LangGraph agent in CLI mode (no AI)...\n")

        queries = [
            "Tell me about Japan – population, capital, and language.",
            "What is the capital of Germany?",
            "Tell me about Brazil.",
        ]
        for query in queries:
            print(f"User: {query}")
            result = agent_executor.invoke(
                {"messages": [HumanMessage(content=query)]},
                config={"configurable": {"thread_id": uuid.uuid4().hex}},
            )
            # Print only the final AI message
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage) and msg.content:
                    print(f"Agent: {msg.content}\n")
                    break
    else:
        print("Starting deterministic LangGraph HTTP server (no AI)...")
        server = from_langgraph(agent_executor)
        server.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        server.run()