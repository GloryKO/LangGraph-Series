"""Tool definitions for the City Events Agent.

Three tools:
  1. events_database_tool — query the local SQLite events database
  2. search_tool          — search the web via Tavily
  3. weather_tool         — fetch live weather via OpenWeatherMap (pyowm)
"""

import json
import os
import sqlite3

from langchain_core.tools import tool
from agent.config import DB_PATH, TAVILY_API_KEY, OPENWEATHERMAP_API_KEY


# ─────────────────────────────────────────────────────────────────────────────
# 1. Local events database
# ─────────────────────────────────────────────────────────────────────────────

@tool
def events_database_tool(city: str) -> str:
    """Query the local SQLite database for events matching a city name.

    Args:
        city: Name of the city to search for (partial matches supported).

    Returns:
        JSON string with matching events or an error message.
    """
    if not os.path.exists(DB_PATH):
        return json.dumps({"error": f"Database not found at {DB_PATH}"})

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM local_events WHERE city LIKE ? LIMIT 10",
            (f"%{city}%",),
        )
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        conn.close()
        events = [dict(zip(cols, row)) for row in rows]
        if not events:
            return json.dumps({"message": f"No events found for '{city}'."})
        return json.dumps({"events": events, "count": len(events)})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ─────────────────────────────────────────────────────────────────────────────
# 2. Web search via Tavily
# ─────────────────────────────────────────────────────────────────────────────

@tool
def search_tool(query: str) -> str:
    """Search the web for information using Tavily.

    Args:
        query: The search query string.

    Returns:
        JSON string with search results or an error message.
    """
    if not TAVILY_API_KEY:
        return json.dumps({"error": "TAVILY_API_KEY not configured in .env"})

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)
        results = client.search(query)
        return json.dumps({"results": results})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ─────────────────────────────────────────────────────────────────────────────
# 3. Weather via pyowm
# ─────────────────────────────────────────────────────────────────────────────

@tool
def weather_tool(city: str) -> str:
    """Fetch current weather for a city using OpenWeatherMap.

    Args:
        city: Name of the city to get weather for.

    Returns:
        JSON string with temperature, humidity, wind, and description.
    """
    if not OPENWEATHERMAP_API_KEY:
        return json.dumps({"error": "OPENWEATHERMAP_API_KEY not configured in .env"})

    try:
        import pyowm

        owm = pyowm.OWM(OPENWEATHERMAP_API_KEY)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather

        weather_data = {
            "city": city,
            "status": w.detailed_status,
            "temperature_celsius": w.temperature("celsius"),
            "humidity": w.humidity,
            "wind": w.wind(),
            "clouds": w.clouds,
        }
        return json.dumps({"weather": weather_data})
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ── Convenience list ─────────────────────────────────────────────────────────
ALL_TOOLS = [events_database_tool, search_tool, weather_tool]
