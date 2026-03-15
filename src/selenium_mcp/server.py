import argparse
import sys
import asyncio

from selenium_mcp.core.mcp_instance import mcp

# Import tools so they register with MCP
from selenium_mcp.tools.browser_tools import *
from selenium_mcp.tools.navigation_tools import *
from selenium_mcp.tools.interaction_tools import *
from selenium_mcp.tools.element_tools import *
from selenium_mcp.tools.page_tools import *
from selenium_mcp.tools.debug_tools import *

from selenium_mcp.utils.logger import logger


VERSION = "1.1.0"


def run_server():
    """Start the MCP server."""
    logger.info("Starting Selenium MCP Server...")
    mcp.run(transport="stdio")


async def sanity_check():
    """Run sanity check and list registered MCP tools."""
    print("\nRunning Selenium MCP Server sanity check...\n")

    try:
        tools = await mcp.list_tools()

        print("Registered MCP Tools")
        print("--------------------")

        tool_names = [tool.name for tool in tools]

        for name in tool_names:
            print(f"- {name}")

        print("\n--------------------")
        print(f"Total tools registered: {len(tool_names)}")

        print("\nMCP Server sanity check passed\n")

    except Exception as e:
        print("\nMCP Server sanity check failed")
        print(str(e))


def show_version():
    """Display version."""
    print(f"Selenium MCP Server v{VERSION}")


def main():
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

    args = parser.parse_args()

    if args.command == "run":
        run_server()

    elif args.command == "check":
        asyncio.run(sanity_check())

    elif args.command == "version":
        show_version()


if __name__ == "__main__":
    main()
