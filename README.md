# Selenium MCP Server

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-Automation-green?logo=selenium)
![MCP](https://img.shields.io/badge/MCP-AI%20Agents-purple)
![Author](https://img.shields.io/badge/Author-Prashant%20Nayak-black)

Model Context Protocol (MCP) server for Selenium WebDriver that enables AI agents and LLMs to control real browsers for automation

This project exposes Selenium WebDriver as an MCP (Model Context Protocol) server, allowing AI agents to control a real browser through structured tools.

It enables LLMs and autonomous agents to perform tasks like:

- Opening browsers
- Navigating websites
- Discovering UI elements
- Clicking buttons and links
- Typing into inputs
- Extracting page text
- Taking screenshots
- Many more future upgrades (in-progress)

This makes it possible to build AI-powered browser automation systems and autonomous QA agents.

## Table of Contents

- [Why This Project Exists](#why-this-project-exists)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [MCP Server Version](#mcp-server-version)
- [Available MCP Tools](#available-mcp-tools)
- [Browser Session Flow](#browser-session-flow)
- [Example Agent Workflow](#example-agent-workflow)
- [System Prompt for AI Agents](#system-prompt-for-ai-agents)
- [Prompt Customization](#prompt-customization)
- [Logging](#logging)
- [Configure Your MCP Client](#configure-your-mcp-client)
- [Requirements](#requirements)
- [Use Cases](#use-cases)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## WHY THIS PROJECT EXISTS

Modern AI agents need a way to interact with real applications.

While traditional automation tools like Selenium exist, they are not directly usable by LLM agents.

This project bridges that gap by exposing Selenium functionality through MCP tools so that agents can:

- Understand web pages
- Discover UI elements
- Perform actions
- Validate results

## ARCHITECTURE

```mermaid
flowchart TD
    A[LLM Agent] --> B[MCP Protocol]
    B --> C[Selenium MCP Server]

    C --> D[Browser Tools]
    C --> E[Navigation Tools]
    C --> F[Interaction Tools]
    C --> G[Element Tools]
    C --> H[Debug Tools]

    D --> I[Selenium WebDriver]
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J[Browser]
```

## FEATURES

- MCP-compatible Selenium automation server
- Browser session management
- Navigation controls
- UI element discovery
- Accessibility-aware interaction
- Screenshot capture
- Page text extraction
- Headless browser support
- Multi-tab browser management (open, switch, close, track active tab)
- Improved interactive element detection for modern UI frameworks (React, Angular, dynamic DOM)

## INSTALLATION

### Run the following command

```bash
pip install selenium-mcp
```

## RUNNING THE SERVER

#### Start the MCP server
You can start the Selenium MCP server using different transport modes depending on your use case.

##### Default (STDIO)
```bash
selenium-mcp run
```

* Uses stdio transport
* Best for local agent integrations
* No network exposure

##### HTTP Mode (Recommended)
```bash
selenium-mcp run --transport http --host 127.0.0.1 --port 3345
```

MCP endpoint: `http://127.0.0.1:3345/mcp`

Best for:
* API integrations
* Postman / curl testing
* production-style usage

##### SSE Mode (Streaming)
```bash
selenium-mcp run --transport sse --host 127.0.0.1 --port 3345
```
SSE endpoint: `http://127.0.0.1:3345/sse`

Best for:
* streaming-based agents
* real-time interactions

Note: Note: SSE endpoints are streaming and may not show output directly in the browser.

##### Expose Server on Network:
```bash
selenium-mcp run --transport http --host 0.0.0.0 --port 3345
```

Makes server accessible from:
* other devices on the same network
* Docker / VM environments

##### Notes:
Default port: `3336`
Supported transports:
```bash
stdio (default)
http
sse
```

Ensure port is within range: `1–65535`

## MCP SERVER VERSION
To check the current version of the selenium MCP server, run the following command:
```bash
selenium-mcp version
```

## AVAILABLE MCP TOOLS

Run the following command to get the list of tools supported by MCP server:
```bash
selenium-mcp tools 
```
This returns the list of tools supported by MCP server.

### BROWSER CONTROL
1. `open_browser` – Launch a new browser session  
2. `close_browser` – Close the browser session  
3. `maximize_browser` – Maximize browser window  
4. `fullscreen_browser` – Switch browser to fullscreen  

### NAVIGATION
1. `open_url` – Navigate to a specific URL  
2. `navigate_back` – Navigate back in browser history  
3. `navigate_forward` – Navigate forward in history  
4. `refresh_page` – Reload the page  
5. `wait_for_page` – Wait for page to load  
6. `get_page_title` – Get the current page title  

### TAB MANAGEMENT
1. `get_tabs` – Retrieve all open tabs in the current session  
2. `switch_tab` – Switch to a specific tab using index  
3. `open_new_tab` – Open a new tab and optionally navigate to a URL  
4. `close_tab` – Close a specific tab by index  
5. `get_current_tab` – Retrieve the currently active tab  
6. `name_tab` – Assign a custom name to a tab for easier identification  

These tools allow agents to manage multiple tabs within a single browser session.

### ELEMENT DISCOVERY
1. `get_interactive_elements` – Discover visible interactive elements on the page  
2. `get_accessibility_tree` – Retrieve simplified accessibility tree for the page  

These tools allow agents to understand the UI structure before interacting with it.

#### Notes
- Element detection is optimized for modern web applications (React, Angular, dynamic UI frameworks).
- Elements are identified using interaction signals such as roles, click handlers, and focusability.
- Only visible and meaningful elements are returned to reduce noise.

### INTERACTION TOOLS
1. `click_element` – Click an element by index  
2. `type_into_element` – Enter text into an input field  

Elements must first be discovered using: `get_interactive_elements`

### PAGE ANALYSIS
`get_page_text` – Extract visible text from the page

Useful for:
- validation
- reasoning
- information extraction

### VISUAL DEBUGGING
`take_screenshot` – Capture a screenshot of the current browser window

#### Screenshot Storage Location
When screenshots are captured, they are automatically saved in a hidden folder inside your home directory.

##### macOS / Linux
Screenshots are stored at:
```
~/.selenium-mcp/screenshot
```

Example full path:
```
/Users/<your-username>/.selenium-mcp/screenshot
```

You can open the folder using Terminal:
```bash
open ~/.selenium-mcp/screenshot
```

##### Windows

Screenshots are stored at:
```
C:\Users\<your-username>\.selenium-mcp\screenshot
```

Example:
```
C:\Users\John\.selenium-mcp\screenshot
```

You can open it from **File Explorer** by entering the following in the address bar:
```
%USERPROFILE%\.selenium-mcp\screenshot
```
#### Custom Screenshot Directory (Optional)

You can override the default screenshot location using the environment variable: `SELENIUM_MCP_SCREENSHOT_DIR`

##### macOS / Linux
```bash
export SELENIUM_MCP_SCREENSHOT_DIR=~/my-screenshots
```

##### Windows (PowerShell)
```bash
$env:SELENIUM_MCP_SCREENSHOT_DIR="C:\my-screenshots"
```

All screenshots will then be saved to the specified directory.

##### Notes

* The folder is **created automatically** the first time a screenshot is taken.
* The `.selenium-mcp` directory is **hidden by default** because it starts with a dot (`.`).
* You can safely delete screenshots anytime.


## BROWSER SESSION FLOW

Each browser session is identified by a `session_id`.

### Typical workflow for agents:
1. open_browser
2. open_url
3. wait_for_page
4. get_interactive_elements
5. (optional) get_tabs / switch_tab if multiple tabs are present
6. click_element or type_into_element

## MULTI-TAB WORKFLOW

Agents can work with multiple tabs within the same browser session.

### Example workflow:
1. open_browser  
2. open_url  
3. open_new_tab("https://example.com")  
4. get_tabs  
5. switch_tab(index)  
6. perform actions  
7. close_tab(index)  

### Notes
- Each tab is tracked using an internal index.
- The active tab is automatically managed and updated.
- All actions are performed on the currently active tab.


## EXAMPLE AGENT WORKFLOW

### Example task: 
1. Open Chrome browser.
2. Navigate to Google.com
3. Type the text "Selenium MCP" in the search box.
4. Press the search button

#### Agent steps:
```python
open_browser
open_url("https://google.com")
wait_for_page
get_interactive_elements
type_into_element(index, "Selenium MCP")
click_element(index)
wait_for_page
get_page_text
```
## SYSTEM PROMPT FOR AI AGENTS

This repository includes a **production-grade system prompt** designed specifically for browser automation agents that interact with this Selenium MCP server.

The prompt contains detailed operational guidelines that instruct the AI agent on how to:

* initialize and control the browser
* discover and interact with UI elements
* analyze page structure using the accessibility tree
* avoid hallucinating element indexes
* handle navigation and page reloads
* recover from stale elements
* follow a deterministic execution loop (PLAN → ACT → OBSERVE → UPDATE PLAN)
* enforce safety limits on tool usage

### Prompt location
```
prompts/system_prompt.md
```

### How to use

Whenever you build an AI agent that interacts with this MCP server, **this prompt should be provided as the system prompt** for the model.


### Why this prompt

Browser automation agents can easily make incorrect decisions if not guided properly.
This system prompt provides **strict operational rules and guardrails** that help the agent:

* use MCP tools correctly
* avoid incorrect element interactions
* minimize hallucinations
* perform reliable browser automation tasks

Using this prompt significantly improves the **stability, accuracy, and reliability** of AI-driven browser automation.

### Recommendation

It is strongly recommended that **all AI agents interacting with this Selenium MCP server use this system prompt** to ensure consistent and reliable behavior.

## PROMPT CUSTOMIZATION

You may modify or extend the system prompt depending on your use case. However, it is recommended to preserve the core operational rules related to:

* MCP tool usage
* element discovery
* navigation handling
* safety limits

## LOGGING
All application logs are stored in a user-specific directory:
```bash
~/.selenium-mcp/logs/
```
This directory is automatically created when the server starts.

### Log file
Logs are written to:
```bash
~/.selenium-mcp/logs/selenium_mcp.log
```

Features:
* Daily log file rotation
* Automatic cleanup of older log files
* Logs written to both console and file
* Persistent logs independent of the project directory

Logs are stored in the user's home directory so they remain available even if the package is installed globally via pip. This makes it easier to debug issues and monitor MCP server activity across different projects.

### Example Log Entry
```bash
2026-03-15 19:00:07,444 [INFO] [selenium-mcp] Initializing Selenium MCP Server...
```

#### macOS / Linux
Logs are stored in:
```bash
/Users/<username>/.selenium-mcp/logs/
```
Example:
```bash
/Users/john/.selenium-mcp/logs/selenium_mcp.log
```
You can open it from the terminal:
```bash
cd ~/.selenium-mcp/logs
ls
```

View logs:
```bash
cat selenium_mcp.log
```
or
```bash
tail -f selenium_mcp.log
```

#### Windows
Logs are stored in:
```bash
C:\Users\<username>\.selenium-mcp\logs\
```
Example:
```bash
C:\Users\John\.selenium-mcp\logs\selenium_mcp.log
```

Open it in File Explorer:
```bash
C:\Users\%USERNAME%\.selenium-mcp\logs\
```

Or from Command Prompt:
```bash
cd %USERPROFILE%\.selenium-mcp\logs
dir
```
## CONFIGURE YOUR MCP CLIENT
Add the Selenium MCP server to your MCP client configuration.

**Example STDIO mode:**
```json
{
  "mcpServers": {
    "selenium-mcp": {
      "command": "selenium-mcp"
    }
  }
}
```
This tells the MCP client how to start the Selenium MCP server using stdio mode.

**Example HTTP mode:**
```json
{
  "mcpServers": {
    "selenium-mcp": {
      "command": "selenium-mcp",
      "args": ["run", "--transport", "http", "host", "127.0.0.1",  "--port", "3345"]
    }
  }
}
```
* Runs MCP server over HTTP
* Endpoint: http://127.0.0.1:3345/mcp

**Example SSE mode:**
```json
{
  "mcpServers": {
    "selenium-mcp": {
      "command": "selenium-mcp",
      "args": ["run", "--transport", "sse", "host", "127.0.0.1", "--port", "3345"]
    }
  }
}
```
* Runs MCP server with streaming (SSE) transport
* Useful for real-time agent interactions
* Endpoint:  http://127.0.0.1:3345/sse

### Client Examples
#### Claude Desktop
Config file location:
##### macOS
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

##### Windows
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

##### STDIO – Works for Claude Desktop
Add
```json
{
  "mcpServers": {
    "selenium-mcp": {
      "command": "selenium-mcp"
    }
  }
}
```
**Restart Claude Desktop after updating the configuration.**

* Uses stdio transport
* Works out of the box with Claude Desktop
* No additional configuration required

### Troubleshooting
If you encounter issues while setting up or running Selenium MCP, try the following solutions.
#### selenium-mcp: command not found

This usually means the CLI command is not available in your system `PATH`.

First verify the package is installed:
```bash
pip show selenium-mcp
```
Locate the installed command.

##### macOS / Linux
```bash
which selenium-mcp
```

Example output:
```bash
/Users/<username>/.local/bin/selenium-mcp
```
If the command is found, update your MCP client configuration to use the full path:
```json
{
  "mcpServers": {
    "selenium-mcp": {
      "command": "/Users/<username>/.local/bin/selenium-mcp"
    }
  }
}
```
##### Windows
Run:
```bash
where selenium-mcp
```
Example output:
```bash
C:\Users\<username>\AppData\Roaming\Python\Python311\Scripts\selenium-mcp.exe
```
Update your MCP client configuration:
```json
{
  "mcpServers": {
    "selenium-mcp": {
      "command": "C:\\Users\\<username>\\AppData\\Roaming\\Python\\Python311\\Scripts\\selenium-mcp.exe"
    }
  }
}
```
Note: Windows paths in JSON require double backslashes (`\\`).

## REQUIREMENTS
* Python 3.10+
* Web browser

## USE CASES

This project can be used to build:
* AI test automation agents
* Autonomous QA assistants
* LLM-powered browser copilots
* Self-healing test frameworks
* AI web scraping agents
* Intelligent UI testing systems

## CONTRIBUTING

Contributions are welcome.

### Steps:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## LICENSE
MIT License

## AUTHOR

Prashant Nayak

🔗 LinkedIn: https://www.linkedin.com/in/prashantjnayak

Built to help the QA and AI automation community build intelligent browser automation systems.

## SUPPORT THE PROJECT

If this project helps you:
* Star the repository
* Share it with the QA community
