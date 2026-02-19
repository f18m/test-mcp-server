"""
Integration tests for the MCP weather server.
Tests that the server starts correctly and responds to client requests.
"""

import asyncio
import os
import subprocess
import time
import pytest
from fastmcp import Client
from fastmcp.client.auth import BearerAuth

# Test configuration
TEST_TOKEN = "test-token-ci"
MCP_URL = "http://localhost:8000/mcp"
MCP_PORT = 8000
SERVER_START_TIMEOUT = 30
BEARER_HEADER = {"Authorization": f"Bearer {TEST_TOKEN}"}


@pytest.fixture(scope="session")
def mcp_server():
    """
    Fixture that starts the MCP server for the entire test session.
    Yields when server is ready, cleans up after tests complete.
    """
    # Set the bearer token environment variable
    env = os.environ.copy()
    env["MCP_BEARER_TOKEN"] = TEST_TOKEN

    # Start the MCP server process
    print("\n📚 Starting MCP server...")
    process = subprocess.Popen(
        ["python", "main.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # await test_mcp_server_connection()
    time.sleep(2)
    # asyncio.run(test_mcp_server_connection())

    # Yield control back to tests
    yield process

    # Cleanup: terminate the server
    print("\n🧹 Stopping MCP server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    print("✓ MCP server stopped")


@pytest.mark.asyncio
async def test_mcp_server_connection(mcp_server):
    """Test that we can connect to the MCP server."""
    client = Client(MCP_URL, auth=BearerAuth(TEST_TOKEN))

    async with client:
        # Verify connection by checking server info
        assert client.initialize_result is not None
        print(
            f"✓ Successfully connected to MCP server: {client.initialize_result.serverInfo.name}"
        )


@pytest.mark.asyncio
async def test_mcp_server_list_tools(mcp_server):
    """Test that the MCP server returns the list of available tools."""
    client = Client(MCP_URL, auth=BearerAuth(TEST_TOKEN))

    async with client:
        # List available tools
        tools = await client.list_tools()

        # Verify we have tools
        assert tools is not None
        assert len(tools) > 0
        print(f"✓ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")


@pytest.mark.asyncio
async def test_mcp_server_get_current_weather_tool(mcp_server):
    """Test that the get_current_weather tool is registered."""
    client = Client(MCP_URL, auth=BearerAuth(TEST_TOKEN))

    async with client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        assert "get_current_weather" in tool_names
        print("✓ get_current_weather tool is registered")


@pytest.mark.asyncio
async def test_mcp_server_get_forecast_tool(mcp_server):
    """Test that the get_forecast tool is registered."""
    client = Client(MCP_URL, auth=BearerAuth(TEST_TOKEN))

    async with client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        assert "get_forecast" in tool_names
        print("✓ get_forecast tool is registered")
