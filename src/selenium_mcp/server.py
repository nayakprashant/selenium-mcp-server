import argparse
import asyncio
import uvicorn

from selenium_mcp.core.mcp_instance import mcp

# Import tools so they register with MCP
from selenium_mcp.tools.browser_tools import *
from selenium_mcp.tools.navigation_tools import *
from selenium_mcp.tools.interaction_tools import *
from selenium_mcp.tools.element_tools import *
from selenium_mcp.tools.page_tools import *
from selenium_mcp.tools.debug_tools import *

from selenium_mcp.utils.logger import logger


VERSION = "1.4.0"


def run_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 3336):
    """Start the MCP server."""
    logger.info(f"Starting Selenium MCP Server with transport={transport}...")

    if not (0 < port < 65536):
        raise ValueError(f"Invalid port: {port}")

    try:
        if transport == "stdio":
            mcp.run(transport="stdio")

        elif transport == "sse":
            logger.info(f"Running SSE server on http://{host}:{port}")

            uvicorn.run(
                mcp.sse_app(),
                host=host,
                port=port,
                log_level="info"
            )

        elif transport == "http":
            logger.info(f"Running HTTP server on http://{host}:{port}")

            uvicorn.run(
                mcp.streamable_http_app(),
                host=host,
                port=port,
                log_level="info"
            )

    except Exception as e:
        logger.exception(
            f"Error encountered while starting the server. Details - {e}")


async def sanity_check():
    """Run sanity check and list registered MCP tools."""
    print("\nRunning Selenium MCP Server sanity check...\n")

    try:
        tools = await mcp.list_tools()

        print("--------------------")
        print("Registered MCP Tools")
        print("--------------------")

        tool_names = [tool.name for tool in tools]

        for name in tool_names:
            print(f"- {name}")

        print("\n-----------------------------")
        print(f"Total tools registered: {len(tool_names)}")
        print("-----------------------------")

        print("\nMCP Server sanity check passed\n")

    except Exception as e:
        print("\nMCP Server sanity check failed")
        print(str(e))


def show_version():
    """Display version."""
    print(f"Selenium MCP Server v{VERSION}")


def main():

    try:
        parser = argparse.ArgumentParser(
            description="Selenium WebDriver MCP server for AI agents and LLM-powered browser automation"
        )

        parser.add_argument(
            "command",
            nargs="?",
            default="run",
            choices=["run", "check", "version"],
            help="Command to run"
        )

        parser.add_argument(
            "--transport",
            choices=["stdio", "sse", "http"],
            default="stdio",
            help="Transport protocol (default: stdio)"
        )

        parser.add_argument(
            "--port",
            type=int,
            default=3336,
            help="Port for SSE, and HTTP transport"
        )

        parser.add_argument(
            "--host",
            type=str,
            default="127.0.0.1",
            help="Host for server (default: 127.0.0.1)"
        )

        args = parser.parse_args()

        if args.command == "run":
            run_server(
                transport=args.transport,
                host=args.host,
                port=args.port
            )

        elif args.command == "check":
            asyncio.run(sanity_check())

        elif args.command == "version":
            show_version()

    except Exception:
        logger.exception(f"MCP server encountered an error")


if __name__ == "__main__":
    main()
