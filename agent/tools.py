"""Tool definitions for the City Events Agent.

Three tools with structured logging, retry logic, and graceful error handling:
  1. events_database_tool — query the local SQLite events database
  2. search_tool          — search the web via Tavily
  3. weather_tool         — fetch live weather via OpenWeatherMap (pyowm)
"""

import json
import os
import sqlite3
import time

from langchain_core.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agent.config import (
    DB_PATH, TAVILY_API_KEY, OPENWEATHERMAP_API_KEY,
    RETRY_MAX_ATTEMPTS, RETRY_WAIT_SECONDS,
)
from agent.log import get_logger

logger = get_logger(__name__)


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
    start = time.monotonic()
    logger.info("tool.events_database.start", city=city)

    if not os.path.exists(DB_PATH):
        logger.error("tool.events_database.db_missing", db_path=DB_PATH)
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
        elapsed = round(time.monotonic() - start, 3)

        if not events:
            logger.info("tool.events_database.no_results", city=city, elapsed_s=elapsed)
            return json.dumps({"message": f"No events found for '{city}'."})

        logger.info("tool.events_database.success", city=city, count=len(events), elapsed_s=elapsed)
        return json.dumps({"events": events, "count": len(events)})
    except Exception as exc:
        logger.error("tool.events_database.error", city=city, error=str(exc))
        return json.dumps({"error": str(exc)})


# ─────────────────────────────────────────────────────────────────────────────
# 2. Web search via Tavily (with retries)
# ─────────────────────────────────────────────────────────────────────────────

def _tavily_search(query: str) -> dict:
    """Inner function with retry logic for Tavily API calls."""
    from tavily import TavilyClient

    @retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_WAIT_SECONDS, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def _call():
        client = TavilyClient(api_key=TAVILY_API_KEY)
        return client.search(query)

    return _call()


@tool
def search_tool(query: str) -> str:
    """Search the web for information using Tavily.

    Args:
        query: The search query string.

    Returns:
        JSON string with search results or an error message.
    """
    start = time.monotonic()
    logger.info("tool.search.start", query=query)

    if not TAVILY_API_KEY:
        logger.warning("tool.search.no_api_key")
        return json.dumps({"error": "TAVILY_API_KEY not configured in .env"})

    try:
        results = _tavily_search(query)
        elapsed = round(time.monotonic() - start, 3)
        logger.info("tool.search.success", query=query, elapsed_s=elapsed)
        return json.dumps({"results": results})
    except Exception as exc:
        elapsed = round(time.monotonic() - start, 3)
        logger.error("tool.search.error", query=query, error=str(exc), elapsed_s=elapsed)
        return json.dumps({"error": str(exc)})


# ─────────────────────────────────────────────────────────────────────────────
# 3. Weather via pyowm (with retries)
# ─────────────────────────────────────────────────────────────────────────────

def _weather_fetch(city: str) -> dict:
    """Inner function with retry logic for OpenWeatherMap API calls."""
    import pyowm

    @retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_WAIT_SECONDS, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def _call():
        owm = pyowm.OWM(OPENWEATHERMAP_API_KEY)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather
        return {
            "city": city,
            "status": w.detailed_status,
            "temperature_celsius": w.temperature("celsius"),
            "humidity": w.humidity,
            "wind": w.wind(),
            "clouds": w.clouds,
        }

    return _call()


@tool
def weather_tool(city: str) -> str:
    """Fetch current weather for a city using OpenWeatherMap.

    Args:
        city: Name of the city to get weather for.

    Returns:
        JSON string with temperature, humidity, wind, and description.
    """
    start = time.monotonic()
    logger.info("tool.weather.start", city=city)

    if not OPENWEATHERMAP_API_KEY:
        logger.warning("tool.weather.no_api_key")
        return json.dumps({"error": "OPENWEATHERMAP_API_KEY not configured in .env"})

    try:
        weather_data = _weather_fetch(city)
        elapsed = round(time.monotonic() - start, 3)
        logger.info("tool.weather.success", city=city, elapsed_s=elapsed)
        return json.dumps({"weather": weather_data})
    except Exception as exc:
        elapsed = round(time.monotonic() - start, 3)
        logger.error("tool.weather.error", city=city, error=str(exc), elapsed_s=elapsed)
        return json.dumps({"error": str(exc)})


# ── Convenience list ─────────────────────────────────────────────────────────
ALL_TOOLS = [events_database_tool, search_tool, weather_tool]
