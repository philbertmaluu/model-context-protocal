#!/usr/bin/env python3
"""
Simple MCP Test Server
Provides basic tools for testing the MCP client
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Create server instance
server = Server("test-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    tools = [
        Tool(
            name="get_time",
            description="Get the current time",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="echo",
            description="Echo back the input message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="add_numbers",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    if name == "get_time":
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Current time: {current_time}"
                )
            ]
        )
    
    elif name == "echo":
        message = arguments.get("message", "")
        return CallToolResult(
            content=[
                TextContent(
                    type="text", 
                    text=f"Echo: {message}"
                )
            ]
        )
    
    elif name == "add_numbers":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"{a} + {b} = {result}"
                )
            ]
        )
    
    else:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )
            ]
        )

async def main():
    """Run the server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="test-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 