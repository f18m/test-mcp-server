"""
Integration tests for the MCP weather server.
Tests that the server starts correctly and responds to client requests.
"""

import asyncio
import os
import subprocess
import time
import pytest
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from mcp.shared._httpx_utils import (
    McpHttpClientFactory,
    create_mcp_http_client,
)

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
    client = create_mcp_http_client(
        headers=BEARER_HEADER,
        auth=None,
    )

    async with streamable_http_client(MCP_URL, http_client=client) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("✓ Successfully connected to MCP server")


@pytest.mark.asyncio
async def test_mcp_server_list_tools(mcp_server):
    """Test that the MCP server returns the list of available tools."""
    client = create_mcp_http_client(
        headers=BEARER_HEADER,
        auth=None,
    )

    async with streamable_http_client(MCP_URL, http_client=client) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()

            # Verify we have tools
            assert tools.tools is not None
            assert len(tools.tools) > 0
            print(f"✓ Found {len(tools.tools)} available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")


@pytest.mark.asyncio
async def test_mcp_server_get_current_weather_tool(mcp_server):
    """Test that the get_current_weather tool is registered."""
    client = create_mcp_http_client(
        headers=BEARER_HEADER,
        auth=None,
    )

    async with streamable_http_client(MCP_URL, http_client=client) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]

            assert "get_current_weather" in tool_names
            print("✓ get_current_weather tool is registered")


@pytest.mark.asyncio
async def test_mcp_server_get_forecast_tool(mcp_server):
    """Test that the get_forecast tool is registered."""
    client = create_mcp_http_client(
        headers=BEARER_HEADER,
        auth=None,
    )

    async with streamable_http_client(MCP_URL, http_client=client) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]

            assert "get_forecast" in tool_names
            print("✓ get_forecast tool is registered")
