"""Interactive CLI for the City Events Agent.

Production features:
  - Correlation IDs per session for log tracing
  - Thread-based conversation memory (multi-turn)
  - Structured logging on every interaction
  - Graceful error handling
"""

import structlog

from agent.config import LOG_LEVEL, LOG_JSON
from agent.log import setup_logging, get_logger, new_correlation_id
from agent.graph import build_graph

logger = get_logger(__name__)


WELCOME_BANNER = """
╔══════════════════════════════════════════════════════════════╗
║              🌆  City Events Agent  🌆                      ║
║                                                              ║
║  I can help you with:                                        ║
║    • Finding local events in cities worldwide                ║
║    • Searching the web for information                       ║
║    • Checking current weather conditions                     ║
║                                                              ║
║  This is a multi-turn conversation — I remember context!     ║
║  Type 'quit' or 'exit' to leave.                             ║
╚══════════════════════════════════════════════════════════════╝
"""


def run_cli():
    """Launch the interactive REPL with production features."""
    # Initialise structured logging
    setup_logging(log_level=LOG_LEVEL, json_output=LOG_JSON)

    # Generate a session-scoped correlation ID
    session_id = new_correlation_id()
    structlog.contextvars.bind_contextvars(session_id=session_id)

    logger.info("cli.session.start", session_id=session_id)

    print(WELCOME_BANNER)

    graph = build_graph()

    # Thread config for conversation memory
    thread_config = {"configurable": {"thread_id": session_id}}

    print("Agent ready. Ask me anything!\n")
    turn_count = 0

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! 👋")
            logger.info("cli.session.end", reason="interrupt", turns=turn_count)
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye! 👋")
            logger.info("cli.session.end", reason="user_exit", turns=turn_count)
            break

        turn_count += 1
        logger.info("cli.user.input", turn=turn_count, length=len(user_input))

        # Invoke the graph with thread memory
        try:
            result = graph.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=thread_config,
            )
            assistant_msg = result["messages"][-1].content
            logger.info("cli.assistant.response", turn=turn_count, length=len(assistant_msg))
            print(f"\nAssistant: {assistant_msg}\n")
        except Exception as exc:
            logger.error("cli.invoke.error", turn=turn_count, error=str(exc))
            print(f"\n❌ Error: {exc}\n")
