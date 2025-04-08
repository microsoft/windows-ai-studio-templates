import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// Create server instance
const server = new McpServer({
  name: "{{SafeProjectNameLowerCase}}",
  version: "1.0.0",
});

server.tool(
  "get_weather",
  "Get weather for a location",
  {
    location: z.string().describe("Location to get weather for, e.g., city name, state, or coordinates"),
  },
  async ({ location }) => {
    if (!location) {
      return {
        content: [
          {
            type: "text",
            text: "Location is required.",
          },
        ],
      };
    }

    // mock weather data
    const conditions = [ "Sunny", "Rainy", "Cloudy", "Snowy" ];
    const weather = {
      location: location,
      temperature: `${Math.floor(Math.random() * 80) + 10}°F`,
      condition: conditions[Math.floor(Math.random() * conditions.length)],
    }
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(weather),
        },
      ],
    };
  }
);

export { server };