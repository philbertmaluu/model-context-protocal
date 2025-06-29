from typing import  Any
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP


#initialize the server
server = FastMCP("weather-server")

#constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-client/1.0"

#define the tools
async def make_nws_request(endpoint: str) -> dict[str, Any] | None:
    """Make a request to the NWS API"""
    headers = {
        "User-Agent": USER_AGENT,   
        "Accept": "application/geo+json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(endpoint, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error: {e}")
        except Exception as e:
            raise Exception(f"Error making request: {e}")



def format_alert(feature: dict) -> str:
    """Format an alert feature"""
    props = feature["properties"]
    return f"""
       Event:  {props.get("event", "Unknown")}
       Area:  {props.get("areaDesc", "Unknown")}
       Severity:  {props.get("severity", "Unknown")}
       Description:  {props.get("description", "No description available")}
       Instruction:  {props.get("instruction", "No instruction available")}
    """


@server.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a given state"""

    """args:  Two-letter state code (e.g. 'CA')
    Returns:  A string containing all active alerts for the given state
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "No alerts found for the given state"

    if not data['features']:
        return "No alerts found for the given state"

    alerts = [format_alert(alert) for alert in data['features']]

    if not alerts:
        return "No alerts found for the given state"

    return "\n\n".join(alerts)


if __name__ == "__main__":
    asyncio.run(server.run())
