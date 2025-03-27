# mcp_server.py
import requests
from mcp.server import Server
from mcp import types
from fastapi import FastAPI, HTTPException
import uvicorn
from sse_starlette.sse import EventSourceResponse
import asyncio
from pydantic import BaseModel

# Initialize MCP Server logic
mcp_server = Server("RandomUserServer")

# Create FastAPI app
app = FastAPI(title="RandomUser MCP Server")

class RandomUserTool:
    def __init__(self):
        self.base_url = "https://randomuser.me/api/"
        requests.packages.urllib3.disable_warnings()

    def _format_user_data(self, user_data):
        try:
            name = f"{user_data['name']['title']} {user_data['name']['first']} {user_data['name']['last']}"
            country = user_data['location']['country']
            age = user_data['dob']['age']
            phone = user_data['phone']
            photo = user_data['picture']['large']
            street = f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}"
            return (
                f"Full Name: {name}\n"
                f"Country: {country}\n"
                f"Age: {age}\n"
                f"Photo: {photo}\n"
                f"Phone: {phone}\n"
                f"Street Address: {street}"
            )
        except KeyError as e:
            return f"Error: Missing data field - {str(e)}"

    def get_random_user(self):
        try:
            response = requests.get(self.base_url, verify=False)
            response.raise_for_status()
            data = response.json()
            return self._format_user_data(data['results'][0])
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed - {str(e)}"

    def get_multiple_users(self, count: int = 5):
        try:
            response = requests.get(f"{self.base_url}?results={count}", verify=False)
            response.raise_for_status()
            data = response.json()
            result = [self._format_user_data(user) for user in data['results']]
            return "\n\n".join(result)
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed - {str(e)}"

    def get_user_by_gender(self, gender: str):
        if gender not in ["male", "female"]:
            return "Error: Gender must be 'male' or 'female'"
        try:
            response = requests.get(f"{self.base_url}?gender={gender}", verify=False)
            response.raise_for_status()
            data = response.json()
            return self._format_user_data(data['results'][0])
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed - {str(e)}"

tool = RandomUserTool()

# Register tools with MCP server
@mcp_server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_random_user",
            description="Fetch a single random user profile.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_multiple_users",
            description="Fetch multiple random user profiles (default 5).",
            inputSchema={
                "type": "object",
                "properties": {"count": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10}},
                "required": []
            }
        ),
        types.Tool(
            name="get_user_by_gender",
            description="Fetch a random user profile by gender.",
            inputSchema={
                "type": "object",
                "properties": {"gender": {"type": "string", "enum": ["male", "female"]}},
                "required": ["gender"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_random_user":
        result = tool.get_random_user()
        return [types.TextContent(type="text", text=result)]
    elif name == "get_multiple_users":
        count = arguments.get("count", 5)
        if not 1 <= count <= 10:
            return [types.TextContent(type="text", text="Error: Count must be between 1 and 10")]
        result = tool.get_multiple_users(count)
        return [types.TextContent(type="text", text=result)]
    elif name == "get_user_by_gender":
        gender = arguments.get("gender")
        if not gender:
            return [types.TextContent(type="text", text="Error: Gender parameter is required")]
        result = tool.get_user_by_gender(gender)
        return [types.TextContent(type="text", text=result)]
    raise ValueError(f"Tool not found: {name}")

# SSE endpoint for MCP (basic connectivity)
async def sse_endpoint():
    async def event_generator():
        yield {"data": f'{{"type": "server_ready", "server": "RandomUserServer"}}'}
        while True:
            await asyncio.sleep(1)
            yield {"data": '{"type": "ping"}'}
    return EventSourceResponse(event_generator())

# Tools list endpoint
@app.get("/mcp/tools")
async def get_tools():
    tools = await list_tools()
    return {"tools": [tool.dict() for tool in tools]}

# Tool call endpoint
class ToolCallRequest(BaseModel):
    name: str
    arguments: dict = {}

@app.post("/mcp/call_tool")
async def call_tool_endpoint(request: ToolCallRequest):
    try:
        result = await call_tool(request.name, request.arguments)
        return {"content": [content.dict() for content in result]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Mount MCP endpoints
app.get("/mcp/sse")(sse_endpoint)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)