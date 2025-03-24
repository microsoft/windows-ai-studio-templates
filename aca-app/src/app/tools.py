import json
import random

def get_weather(location):
# mock implementation that returns a random weather condition
    return random.choice([
        "Sunny, a very nice day",
        "Rainy, but not cold",
        "Cloudy, and a bit colde",
        "Windy, warmly windy",
        "Snowy, very very heavy snow"
    ])

tools = {
    "get_weather": get_weather
}

def call_tool(name, args):
    try:
        args_obj = json.loads(args)
    except json.JSONDecodeError:
        return f"Tool call args is invalid JSON"
    if name in tools:
        return tools[name](*list(args_obj.values()))
    else:
        return f"Tool {name} not found"