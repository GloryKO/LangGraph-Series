# LangGraph City Events Agent

A clean, modular, and extensible agentic system built with [LangGraph](https://github.com/langchain-ai/langgraph) and LangChain. 
This agent acts as a specialized assistant that can intelligently route requests to different active tools to fetch information.

## ✨ Features
The agent utilizes an LLM backbone (configurable via `.env`) and is equipped with three data-retrieval tools:
1. **Local Events Database Tool**: Queries a local SQLite database for city events.
2. **Web Search Tool**: Performs real-time web searches using the [Tavily Search API](https://tavily.com/).
3. **Live Weather Tool**: Fetches actual, live weather using OpenWeatherMap (via `pyowm`).

The architecture strictly uses **Pydantic DTOs** for tool schemas to guarantee clean, strictly typed interfaces.

---

## 🚀 Quickstart

### 1. Prerequisites
You need Python 3.10+ installed. Virtual environments are highly recommended.

### 2. Install Dependencies
Install all the required packages pinned in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Ensure you have a `.env` file in the root of the project. You must supply your choice of LLM API key and keys for the tools.

Example `.env`:
```env
# Choose your preferred LLM model string. By default, it's set to openai:gpt-4o-mini
MODEL_NAME=openai:gpt-4o-mini
# Or optionally:
# MODEL_NAME=google_genai:gemini-2.0-flash

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
```

### 4. Initialize the Data
Before running the agent, initialize the local events SQLite repository:
```bash
python scripts/create_db.py
```
This will read the `data/events_db.json` seed data and bootstrap a local SQLite database located at `data/local_info.db`.

### 5. Run the Agent
Run the main script to start an interactive Command-Line Interface (CLI) loop:
```bash
python main.py
```
You can then talk to the agent in plain English! Try prompts like:
- *"What's the weather in Miami?"* (Triggers the PyOWM Weather tool)
- *"Find upcoming events in Tokyo"* (Queries the local SQLite database)
- *"Search the web for the latest artificial intelligence news"* (Triggers the Tavily search tool)

Type `quit` or `exit` to shut down the agent.

---

## 🏗️ Project Architecture

```
LangGraphTutorial/
├── agent/                  # Core Agent logic
│   ├── config.py           # Loads environment configurations & `.env`
│   ├── state.py            # LangGraph TypedDict state definitions
│   ├── tools.py            # All tools and their Pydantic DTO schemas
│   ├── graph.py            # Graph construction & orchestration
│   └── cli.py              # Interactive interactive REPL interface
├── scripts/                # Utility scripts
│   └── create_db.py        # Bootstraps the local SQLite DB from JSON data
├── data/                   # Data sources
│   ├── events_db.json      # Structured seed JSON definitions
│   └── local_info.db       # Generated SQLite database (created via scripts/create_db.py)
├── requirements.txt        # Strictly pinned dependencies 
├── .env                    # Secrets & keys (git ignored)
└── main.py                 # Application Entrypoint
```
