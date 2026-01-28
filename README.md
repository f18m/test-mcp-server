# MCP Weather Server

A Model Context Protocol (MCP) server that provides weather data using the Open-Meteo API with Bearer Token authentication.

## Features

- **Get Current Weather**: Fetch real-time weather conditions for any location
- **Get Forecast**: Get 1-16 day weather forecasts
- **Bearer Token Authentication**: Secure access with token-based authentication
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Prerequisites

- Python 3.14+ (for local development)
- Docker & Docker Compose (for containerized deployment)
- MCP Bearer Token (for authentication)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd test-mcp-server
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set the Bearer token:
```bash
export MCP_BEARER_TOKEN="your-secret-token-here"
```

5. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000/mcp`

## Docker Deployment

### Using Docker

1. Build the image:
```bash
docker build -t mcp-weather-server .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e MCP_BEARER_TOKEN="your-secret-token" mcp-weather-server
```

### Using Docker Compose (Recommended)

Create a `docker-compose.yml` file in your project root:

```yaml
version: '3.8'

services:
  mcp-weather:
    build: .
    container_name: mcp-weather-server
    ports:
      - "8000:8000"
    environment:
      MCP_BEARER_TOKEN: ${MCP_BEARER_TOKEN:-default-secret-token-change-me}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "-H", "Authorization: Bearer ${MCP_BEARER_TOKEN:-default-secret-token-change-me}", "http://localhost:8000/mcp"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

1. Create a `.env` file with your token:
```bash
cat > .env << EOF
MCP_BEARER_TOKEN=your-secret-token-here
EOF
```

2. Start the server:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f mcp-weather
```

4. Stop the server:
```bash
docker-compose down
```

## Usage

### Authentication

All requests require Bearer Token authentication:

```bash
curl -H "Authorization: Bearer your-secret-token" http://localhost:8000/mcp
```

### Connecting MCP Clients

#### Using MCP Inspector

1. Set the server URL: `http://localhost:8000/mcp`
2. Add Authorization header: `Bearer your-secret-token`

#### Using Python MCP Client

```python
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

headers = {"Authorization": "Bearer your-secret-token"}

async with streamable_http_client("http://localhost:8000/mcp", headers=headers) as (read_stream, write_stream, _):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")
```

### Available Tools

#### `get_current_weather`
Get current weather conditions for a location.

**Parameters:**
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

**Example:**
```python
result = await session.call_tool("get_current_weather", latitude=40.7128, longitude=-74.0060)
```

#### `get_forecast`
Get weather forecast for a location.

**Parameters:**
- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location
- `days` (int): Number of days to forecast (1-16, default: 7)

**Example:**
```python
result = await session.call_tool("get_forecast", latitude=40.7128, longitude=-74.0060, days=5)
```

## Testing

### Run Tests Locally

```bash
pip install pytest pytest-asyncio requests
pytest tests/ -v
```

### Test Coverage

The test suite includes:
- Server startup and initialization
- Bearer token authentication validation
- MCP tool listing and verification
- Integration tests with MCP client

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_BEARER_TOKEN` | Bearer token for authentication | `default-secret-token-change-me` |

### Server Configuration

The server listens on:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8000`
- **Endpoint**: `/mcp`

## Docker Compose Network Access

To make the server accessible from other containers or hosts:

### Access from localhost:
```bash
docker-compose up
curl -H "Authorization: Bearer your-token" http://localhost:8000/mcp
```

### Access from other containers:
```yaml
# In another docker-compose.yml or service
services:
  other-service:
    depends_on:
      - mcp-weather
    environment:
      MCP_SERVER_URL: http://mcp-weather:8000/mcp
```

### Access from host machine (when running on remote server):
```bash
curl -H "Authorization: Bearer your-token" http://<server-ip>:8000/mcp
```

## CI/CD

This project includes GitHub Actions CI pipeline that:
- Lints Python code (black, isort, flake8, pylint)
- Type checks with mypy
- Builds and pushes Docker image to ghcr.io
- Runs integration tests with pytest

See `.github/workflows/ci.yml` for details.

## Troubleshooting

### Server won't start

Check server logs:
```bash
docker-compose logs -f mcp-weather
```

### Authentication errors

Verify the Bearer token is set correctly:
```bash
echo $MCP_BEARER_TOKEN
```

Update the token in `.env` file and restart:
```bash
docker-compose down && docker-compose up -d
```

### Connection refused

Ensure the container is running:
```bash
docker-compose ps
```

And the port mapping is correct:
```bash
docker-compose port mcp-weather 8000
```

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
