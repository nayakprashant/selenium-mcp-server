# selenium-mcp-server
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Selenium](https://img.shields.io/badge/selenium-automation-green)
![MCP](https://img.shields.io/badge/MCP-AI%20Agents-purple)

Selenium WebDriver MCP server that enables LLMs & AI agents to control real browsers using Selenium and MCP.

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

## WHY THIS PROJECT EXISTS

Modern AI agents need a way to interact with real applications.

While traditional automation tools like Selenium exist, they are not directly usable by LLM agents.

This project bridges that gap by exposing Selenium functionality through MCP tools so that agents can:

- Understand web pages
- Discover UI elements
- Perform actions
- Validate results

## ARCHITECTURE

AI Agent / LLM --> MCP Protocol --> Selenium MCP Server --> Selenium WebDriver --> Web Browser

## FEATURES

- MCP-compatible Selenium automation server
- Browser session management
- Navigation controls
- UI element discovery
- Accessibility-aware interaction
- Screenshot capture
- Page text extraction
- Headless browser support

## INSTALLATION

### Clone the repository

```bash
git clone https://github.com/nayakprashant/selenium-mcp-server.git

cd selenium-mcp-server
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the environment

#### Mac / Linux
```bash
source .venv/bin/activate
```

#### Windows
```bash
.venv\Scripts\activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## ENVIRONMENT CONFIGURATION

Create a .env file in the root of the project.

Add the following variable:
```python
MCP_SCREENSHOT_DIR=/path/to/screenshot/directory
```

### Example:
```python
MCP_SCREENSHOT_DIR=/Users/yourname/screenshots
```
This variable defines the directory where screenshots captured by the take_screenshot tool will be saved.

Make sure the directory exists, and the application has permission to write files to it.

## RUNNING THE SERVER

#### Start the MCP server
```bash
python server.py
```
This launches the Selenium MCP server and exposes browser automation tools to AI agents.

## BROWSER SESSION FLOW

Each browser session is identified by a session_id.

### Typical workflow for agents:
1. open_browser
2. open_url
3. wait_for_page
4. get_interactive_elements
5. click_element or type_into_element

## AVAILABLE MCP TOOLS
### BROWSER CONTROL
1. open_browser – Launch a new browser session  
2. close_browser – Close the browser session  
3. maximize_browser – Maximize browser window  
4. fullscreen_browser – Switch browser to fullscreen  

### NAVIGATION
1. open_url – Navigate to a specific URL  
2. navigate_back – Navigate back in browser history  
3. navigate_forward – Navigate forward in history  
4. refresh_page – Reload the page  
5. wait_for_page – Wait for page to load  
6. get_page_title – Get the current page title  

### ELEMENT DISCOVERY
1. get_interactive_elements – Discover visible interactive elements on the page  
2. get_accessibility_tree – Retrieve simplified accessibility tree for the page  

These tools allow agents to understand the UI structure before interacting with it.

### INTERACTION TOOLS
1. click_element – Click an element by index  
2. type_into_element – Enter text into an input field  

Elements must first be discovered using:
get_interactive_elements

### PAGE ANALYSIS
get_page_text – Extract visible text from the page

Useful for:
- validation
- reasoning
- information extraction

### VISUAL DEBUGGING
take_screenshot – Capture a screenshot of the current browser window

Screenshots are saved to the system temporary directory by default.

To change the location, set the environment variable:
```python
MCP_SCREENSHOT_DIR
```
## EXAMPLE AGENT WORKFLOW

### Example task: 
Search Google for "Selenium MCP"

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

## REQUIREMENTS
- Python 3.10+
- Selenium
- Web browser
- webdriver-manager
- MCP Python SDK

## USE CASES

This project can be used to build:
- AI test automation agents
- Autonomous QA assistants
- LLM-powered browser copilots
- Self-healing test frameworks
- AI web scraping agents
- Intelligent UI testing systems

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
- Star the repository
- Share it with the QA community
