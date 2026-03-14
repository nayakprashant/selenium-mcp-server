import asyncio
import json
import os

from openai import OpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


async def main():

    server = StdioServerParameters(
        command="python3",
        args=["server.py"]
    )

    async with stdio_client(server) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            # Get tools from MCP
            tools = await session.list_tools()

            tool_defs = []

            amazon_workflow = "" \
                "1. Open Firefox browser and maximize it." \
                "2. Navigate to https://www.amazon.in/" \
                "3. Capture the screenshot of the page" \
                "4. Close the browser"

            angular_demo = "" \
                "1. Open Chrome browser and maximize it." \
                "2. Navigate to https://material.angularjs.org/latest/demo/menu" \
                "3. From the left hand side menu option - Click on 'Introduction and Terms' under 'THEMING." \
                "4. Inside the main page on RHS, locate 'Theming Approach' header and click on it." \
                "5. Under 'Important Terms', locate the text 'Palettes' and click on it."

            regulat_html_practice = "You are an expert selenium automation QA tester. Perform following task step by step:"
            "1. Open chrome browser and maximize it."
            "2. Navigate to https://practicetestautomation.com/practice-test-login/. "
            "3. Click on 'Practice' link from the header menu."
            "4. Click on 'Test Exceptions' link."
            "5. Scroll all the way to the bottom."
            "6. Click on back button of the browser."
            "7. Click on 'Test Login Page' link."
            "8. Enter 'student' as username."
            "9. Enter 'Password123' for password field."
            "10. Click on Submit button."
            "11. Click on 'Logout' button."
            "12. Navigate to 'https://practicetestautomation.com/practice-test-table/' url in the same browser instance."
            "13. Take your time and think & reason properly before performing the following step - "
            "- Under 'Automation Courses' header, there is a table. The table has ID and Link columns (among many others)."
            "- Click on 'View' link for the course having ID as '1517620'."
            "14. Close the browser."

            for tool in tools.tools:
                tool_defs.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            messages = [
                {"role": "system",
                 "content":
                 "You are an AI browser automation agent. You control a browser using MCP tools. Follow these rules strictly:"
                 "1. Always open a browser session first using open_browser."
                 "2. After navigating to a page, always call wait_for_page."
                 "3. You may call get_accessibility_tree to analyze and understand the UI structure of the page. "
                 "4. The accessibility tree is ONLY for analysis and understanding the page."
                 "5. Never perform actions using indexes or elements from get_accessibility_tree."
                 "6. Once the page is loaded completely, call get_interactive_elements to discover UI elements."
                 "7. Before clicking or typing, ensure you make use of the UI elements returned by get_interactive_elements"
                 "8. Use click_element(index) to click elements."
                 "9. Use type_into_element(index, text) to enter text into inputs."
                 "10. If the page changes after clicking, call wait_for_page again, and call get_interactive_elements to discover UI elements."
                 "11. Never guess element indexes without first retrieving interactive elements."
                 " When selecting an element:"
                 "- Prefer elements with clear text or placeholder values."
                 "- Avoid selecting generic elements unless necessary."
                 "- Always confirm the element index exists. "
                 "Continue interacting with the page until the task is completed."
                 "12. Once you start working on the task, do not wait for any response. I won't be available to answer."
                 "Proceed as instructed"
                 },
                {
                    "role": "user",
                    "content": f"{angular_demo}"
                }
            ]

            while True:

                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    tools=tool_defs
                )

                msg = response.choices[0].message

                if msg.tool_calls:

                    tool_call = msg.tool_calls[0]

                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    print("Calling tool:", tool_name, arguments)

                    result = await session.call_tool(tool_name, arguments)

                    messages.append(msg)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text
                    })

                else:

                    print(msg.content)
                    break


asyncio.run(main())
