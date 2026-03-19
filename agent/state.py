"""Agent state definition."""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    """Graph state carrying the conversation messages.

    The `add_messages` reducer appends new messages instead of overwriting,
    which is the standard LangGraph pattern for chat-style agents.
    """
    messages: Annotated[list, add_messages]
