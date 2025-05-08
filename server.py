from fastmcp import FastMCP, Context
from ibapi_functions import get_portfolio, check_gateway_connection

# Create a FastMCP server
mcp = FastMCP("IB Gateway MCP Server")

@mcp.tool()
def get_portfolio_tool(host: str = "127.0.0.1", port: int = 4001, client_id: int = 100) -> str:
    """
    Retrieve portfolio information from Interactive Brokers.
    
    Args:
        host: The host address of the IB Gateway/TWS (default: 127.0.0.1)
        port: The port of the IB Gateway/TWS (default: 4001)
        client_id: The client ID to use for the connection (default: 100)
        
    Returns:
        A formatted string containing account summary and positions information
    """
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
        for position in positions:
            contract = position["contract"]
            result += f"### {contract['symbol']} ({contract['secType']})\n\n"
            result += f"- Exchange: {contract['exchange']}\n"
            result += f"- Currency: {contract['currency']}\n"
            result += f"- Position: {position['pos']}\n"
            result += f"- Average Cost: {position['avgCost']}\n\n"
    else:
        result += "No positions found.\n\n"
    
    return result

@mcp.resource("ibgateway://{host}/{port}")
def get_gateway_status(host: str = "127.0.0.1", port: int = 4001) -> str:
    """Get the current status of the IB Gateway connection"""
    
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

## Connection Parameters

- Default Host: 127.0.0.1
- Default Port: 4001 (TWS Paper: 7497, TWS Live: 7496)
- Default Client ID: 100

Make sure your IB Gateway or TWS is running and logged in before using these tools.
"""
    
    return result

if __name__ == "__main__":
    import sys
    
    # Check if "sse" is in command line arguments
    if len(sys.argv) > 1 and "sse" in sys.argv:
        # Run with SSE transport on default port 8000
        port = 8000
        # Check if a port is specified (format: "port=XXXX")
        for arg in sys.argv:
            if arg.startswith("port="):
                try:
                    port = int(arg.split("=")[1])
                except (ValueError, IndexError):
                    print(f"Invalid port format: {arg}. Using default port 8000.")
        
        print(f"Starting server with SSE transport on port {port}...")
        mcp.run(transport="sse", port=port)
    else:
        # Default: run with stdio transport
        print("Starting server with stdio transport...")
        mcp.run()
