"""Interactive CLI for the City Events Agent."""

from agent.graph import build_graph


WELCOME_BANNER = """
╔══════════════════════════════════════════════════════════════╗
║              🌆  City Events Agent  🌆                      ║
║                                                              ║
║  I can help you with:                                        ║
║    • Finding local events in cities worldwide                ║
║    • Searching the web for information                       ║
║    • Checking current weather conditions                     ║
║                                                              ║
║  Type 'quit' or 'exit' to leave.                             ║
╚══════════════════════════════════════════════════════════════╝
"""


def run_cli():
    """Launch the interactive REPL."""
    print(WELCOME_BANNER)

    graph = build_graph()
    print("Agent ready. Ask me anything!\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! 👋")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye! 👋")
            break

        # Invoke the graph
        try:
            result = graph.invoke(
                {"messages": [{"role": "user", "content": user_input}]}
            )
            assistant_msg = result["messages"][-1].content
            print(f"\nAssistant: {assistant_msg}\n")
        except Exception as exc:
            print(f"\n❌ Error: {exc}\n")
