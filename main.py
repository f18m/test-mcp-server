"""
Simple MCP server providing weather data using the Open-Meteo API.
Requires an environment variable MCP_BEARER_TOKEN to be set for authentication.

Tested successfully to work with the OpenWebUI tool.
"""

from typing import Any
import os
import httpx
from fastmcp import FastMCP
from fastmcp.server.auth.providers.debug import DebugTokenVerifier
from fastmcp.server.middleware import PingMiddleware

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Authentication configuration
# Set your Bearer token via environment variable: export MCP_BEARER_TOKEN="your-secret-token" or put it in a .env file
BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN", "default-secret-token-change-me")


# Custom token validation function
async def validate_token(token: str) -> bool:
    """Validate bearer token against environment variable."""
    # print(f"Verifying received token: {token}")
    return token == BEARER_TOKEN


# Initialize authentication provider
auth = DebugTokenVerifier(
    validate=validate_token, client_id="default-client", scopes=["user"]
)

# Initialize FastMCP server
mcp = FastMCP(
    name="weather",
    auth=auth,
)
mcp.add_middleware(PingMiddleware(interval_ms=5000))


# Constants
OPENMETEO_API_BASE = "https://api.open-meteo.com/v1"
USER_AGENT = "weather-app/1.0"


# Helper function to make a request to the Open-Meteo API
async def make_openmeteo_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Open-Meteo API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_current_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """

    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,is_day,showers,cloud_cover,wind_speed_10m,wind_direction_10m,pressure_msl,snowfall,precipitation,relative_humidity_2m,apparent_temperature,rain,weather_code,surface_pressure,wind_gusts_10m"

    data = await make_openmeteo_request(url)
    if not data:
        return "Unable to fetch current weather data for this location."

    # print(f"✓ Fetched current weather data for ({latitude}, {longitude}): {data}")
    return data.__str__()


@mcp.tool()
async def get_forecast(latitude: float, longitude: float, days: int = 7) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        days: Number of days to forecast (1-16, default: 7)
    """
    # Clamp days to valid range
    days = max(1, min(16, days))

    url = f"{OPENMETEO_API_BASE}/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,weather_code&forecast_days={days}&timezone=auto"

    data = await make_openmeteo_request(url)
    if not data:
        return f"Unable to fetch forecast data for this location."

    return data.__str__()


if __name__ == "__main__":
    # Initialize and run the server
    # please note that you need to connect to
    #    <IP>:8000/mcp
    # to access the MCP server
    # with Authorization header: Bearer <your-token>
    mcp.run(transport="http", host="0.0.0.0", port=8000)
