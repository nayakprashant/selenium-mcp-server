import subprocess
import json
import sys
import time

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

print("Initialize response:")
print(receive())

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

print("Tools list:")
print(receive())
