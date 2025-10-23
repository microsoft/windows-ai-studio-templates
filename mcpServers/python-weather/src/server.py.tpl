import json
import random
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
server = FastMCP("{{SafeProjectNameLowerCase}}")

@server.tool(
    name="get_weather",
    title="Get Weather",
    description="Get weather information for a given location"
)
async def get_weather(location: str) -> str:
    """Get weather information for a given location.

    Args:
        location: Location to get weather for, e.g., city name, state, or coordinates
    
    """
    if not location:
        return "Location is required."
    
    # mock weather data
    conditions = [ "Sunny", "Rainy", "Cloudy", "Snowy" ]
    weather = {
        "location": location,
        "temperature": f"{random.randint(10, 90)}°F",
        "condition": random.choice(conditions),
    }
    return json.dumps(weather, ensure_ascii=False)
