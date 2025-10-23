import os
import sys
from server import server

if __name__ == "__main__":
    """Main entry point"""
    transport_type = sys.argv[1] if len(sys.argv) > 1 else None
    server.settings.log_level = os.environ.get("LOG_LEVEL", "DEBUG")
    if transport_type == "http":
        port = int(os.environ.get("PORT", 3001))
        server.settings.port = port
        server.settings.host = "127.0.0.1"
        server.run(transport="streamable-http")
    elif transport_type == "stdio":
        server.run(transport="stdio")
    else:
        print("Invalid transport type. Use 'http' or 'stdio'.")
        sys.exit(1)