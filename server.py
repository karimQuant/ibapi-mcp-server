import os
from fastmcp import FastMCP, Context
from ibapi_mcp_server.ibapi_functions import get_portfolio, check_gateway_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a FastMCP server
mcp = FastMCP("IB Gateway MCP Server")

@mcp.tool()
def get_portfolio_tool() -> str:
    """
    Retrieve portfolio information from Interactive Brokers using environment variables.
    
    Returns:
        A formatted string containing account summary and positions information
    """
    host = os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
    port = int(os.getenv("IB_GATEWAY_PORT", "4001"))
    client_id = int(os.getenv("IB_GATEWAY_CLIENT_ID", "100"))
    
    account_summary, positions = get_portfolio(host, port, client_id)
    
    # Format the response
    result = "# Portfolio Information\n\n"
    
    # Account Summary
    result += "## Account Summary\n\n"
    for account, details in account_summary.items():
        result += f"### Account: {account}\n\n"
        for tag, value in details.items():
            result += f"- {tag}: {value}\n"
        result += "\n"
    
    # Positions
    result += "## Positions\n\n"
    if positions:
        # Sort positions by ticker symbol and then by maturity date
        sorted_positions = sorted(positions, key=lambda p: (p['contract']['symbol'], p['contract'].get('lastTradeDateOrContractMonth', '')))
        for position in sorted_positions:
            contract = position["contract"]
            result += f"### {contract['symbol']} ({contract['secType']})\n\n"
            result += f"- Currency: {contract['currency']}\n"
            result += f"- Position: {position['pos']}\n"
            result += f"- Maturity (YYYMMDD): {contract['lastTradeDateOrContractMonth']}\n"
            result += f"- Strike: {contract['strike']}\n"
            result += f"- Multiplier: {contract['multiplier']}\n"
            result += f"- Right (Call/Put): {contract['right']}\n"
            result += f"- Average Cost: {position['avgCost']}\n\n"
    else:
        result += "No positions found.\n\n"
    
    return result

@mcp.resource("ibgateway://status")
def get_gateway_status() -> str:
    """Get the current status of the IB Gateway connection using environment variables"""
    
    # Get connection parameters from environment variables
    host = os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
    port = int(os.getenv("IB_GATEWAY_PORT", "4001"))
    
    # Check if the gateway is connected
    status = check_gateway_connection(host, port)
    
    # Format the response
    result = "# IB Gateway Status\n\n"
    
    if status["connected"]:
        result += f"✅ **Connected** to IB Gateway/TWS at {status['host']}:{status['port']}\n\n"
    else:
        result += f"❌ **Not Connected** to IB Gateway/TWS at {status['host']}:{status['port']}\n\n"
        result += f"Error: {status.get('error', 'Unknown error')}\n\n"
        result += "Please make sure your IB Gateway or TWS is running and logged in.\n\n"
    
    result += """
## Available Tools

- **get_portfolio_tool**: Retrieve your current portfolio positions and account summary

## Connection Parameters (from environment variables)

- Host: """ + os.getenv("IB_GATEWAY_HOST", "127.0.0.1") + """
- Port: """ + os.getenv("IB_GATEWAY_PORT", "4001") + """ (TWS Paper: 7497, TWS Live: 7496)
- Client ID: """ + os.getenv("IB_GATEWAY_CLIENT_ID", "100") + """

Make sure your IB Gateway or TWS is running and logged in before using these tools.
"""
    
    return result

if __name__ == "__main__":
    import sys
    
    # Check if "sse" is in command line arguments
    if len(sys.argv) > 1 and "sse" in sys.argv:
        # Get host and port from environment variables with defaults
        host = os.getenv("SERVER_HOST", "127.0.0.1")
        default_port = 8000
        env_port = os.getenv("SERVER_PORT")
        port = int(env_port) if env_port else default_port
        
        # Check if a port is specified in command line (format: "port=XXXX")
        for arg in sys.argv:
            if arg.startswith("port="):
                try:
                    port = int(arg.split("=")[1])
                except (ValueError, IndexError):
                    print(f"Invalid port format: {arg}. Using port {port}.")
        
        print(f"Starting server with SSE transport on {host}:{port}...")
        mcp.run(transport="sse", host=host, port=port)
    else:
        # Default: run with stdio transport
        print("Starting server with stdio transport...")
        mcp.run()
