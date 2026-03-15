import subprocess
import json
import sys
import time
from utils.logger import logger

logger.info("Selenium MCP Server Test Status: STARTED")

proc = subprocess.Popen(
    [sys.executable, "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)


def send(msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()


def receive():
    return proc.stdout.readline()


# STEP 1: Initialize MCP session
send({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "clientInfo": {
            "name": "mcp-test-client",
            "version": "1.0"
        },
        "capabilities": {}
    }
})

receive()

# STEP 2: Send initialized notification
send({
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
})

time.sleep(1)

# STEP 3: List tools
send({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
})

tool_list = []

response = receive()
data = json.loads(response)

tools = data["result"]["tools"]

for tool in tools:
    tool_list.append(tool["name"])

logger.info(f"List of tools available: {tool_list}")

if len(tools) > 0:
    logger.info(f"Selenium MCP Server Test Status: SUCCESS")
else:
    logger.error(f"Selenium MCP Server Test Status: FAILED")
