"""
Simple MCP server providing weather data using the Open-Meteo API.
Requires an environment variable MCP_BEARER_TOKEN to be set for authentication.

Tested successfully to work with the OpenWebUI tool.
"""

from typing import Any
import os
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.server.auth.settings import AuthSettings
from mcp.server.auth.provider import AccessToken, TokenVerifier 
from pydantic import AnyHttpUrl # type:ignore

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EnvironmentTokenVerifier(TokenVerifier):
    "Token verifier che mappa token univoci ai client_id."

    async def verify_token(self, token: str) -> AccessToken | None:
        # Authentication configuration
        # Set your Bearer token via environment variable: export MCP_BEARER_TOKEN="your-secret-token" or put it in a .env file
        BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN", "default-secret-token-change-me")

        #print(f"Verifying received token: {token}")
        if token == BEARER_TOKEN:
            access_token = AccessToken(
                token=token,
                client_id="default-client",
                scopes=["user"]
            )
            return access_token
        
        return None

# Initialize FastMCP server
mcp = FastMCP(
    "weather",
    json_response=True,  # Enables stateless mode for better compatibility

    # Token verifier for authentication
    token_verifier=EnvironmentTokenVerifier(),
    # Auth settings for RFC 9728 Protected Resource Metadata
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.example.com"),  # Authorization Server URL
        resource_server_url=AnyHttpUrl("http://localhost:8000"),  # This server's URL
        required_scopes=["user"],
    ),

    # see https://github.com/modelcontextprotocol/python-sdk/issues/1798
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

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
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    
    # please note that you need to connect to
    #    <IP>:8000/mcp 
    # to access the MCP server
    # with Authorization header: Bearer <your-token>
    mcp.run(transport="streamable-http")
