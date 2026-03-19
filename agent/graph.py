"""LangGraph graph construction for the City Events Agent."""

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from agent.config import MODEL_NAME
from agent.state import State
from agent.tools import ALL_TOOLS


def build_graph():
    """Build and compile the agent graph.

    Architecture:
        START → chatbot ←→ tools
                  ↓
                 END

    The chatbot node calls the LLM (with tools bound). If the LLM decides
    to call a tool, the `tools_condition` edge routes to the `tools` node,
    which executes the tool and loops back to the chatbot. Otherwise, the
    conversation ends.

    Returns:
        A compiled LangGraph `CompiledGraph`.
    """
    # Initialise the LLM with tools bound
    llm = init_chat_model(MODEL_NAME)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def chatbot(state: State):
        """Invoke the LLM on the current message history."""
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    # Build the state graph
    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    # Edges
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    return builder.compile()
