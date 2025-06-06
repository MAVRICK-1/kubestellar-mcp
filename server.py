import asyncio
import json
from typing import Any, Dict, List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from utils.logger import setup_logger

from config.settings import settings

logger = setup_logger(__name__)

# Initialize the MCP server
server = Server(settings.server_name)




async def main():
    """Main entry point for the server."""
    # Server configuration
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=settings.server_name,
                server_version=settings.server_version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    asyncio.run(main())