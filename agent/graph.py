"""LangGraph graph construction for the City Events Agent.

Production features:
  - Conversation memory via MemorySaver (thread-scoped)
  - Structured logging on every LLM invocation
  - Execution timing for observability
"""

import time
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from agent.config import MODEL_NAME
from agent.state import State
from agent.tools import ALL_TOOLS
from agent.log import get_logger

logger = get_logger(__name__)


def build_graph():
    """Build and compile the agent graph with conversation memory.

    Architecture:
        START → chatbot ←→ tools
                  ↓
                 END

    The chatbot node calls the LLM (with tools bound). If the LLM decides
    to call a tool, the `tools_condition` edge routes to the `tools` node,
    which executes the tool and loops back to the chatbot. Otherwise, the
    conversation ends.

    Conversation memory is maintained per-thread via LangGraph's MemorySaver,
    allowing multi-turn conversations within the same session.

    Returns:
        A compiled LangGraph `CompiledGraph` with memory checkpointing.
    """
    logger.info("graph.build.start", model=MODEL_NAME, tool_count=len(ALL_TOOLS))

    # Initialise the LLM with tools bound
    llm = init_chat_model(MODEL_NAME)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def chatbot(state: State):
        """Invoke the LLM on the current message history."""
        start = time.monotonic()
        msg_count = len(state.get("messages", []))
        logger.info("graph.chatbot.invoke", message_count=msg_count)

        response = llm_with_tools.invoke(state["messages"])

        elapsed = round(time.monotonic() - start, 3)
        has_tool_calls = bool(getattr(response, "tool_calls", None))
        logger.info(
            "graph.chatbot.response",
            elapsed_s=elapsed,
            has_tool_calls=has_tool_calls,
        )
        return {"messages": [response]}

    # Build the state graph
    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    # Edges
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    # Compile with conversation memory
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    logger.info("graph.build.complete", nodes=list(builder.nodes))
    return graph
