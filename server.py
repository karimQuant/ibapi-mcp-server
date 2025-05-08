from mcp.server.fastmcp import FastMCP, Context
from ibapi_functions import get_portfolio

# Create an MCP server
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

@mcp.resource("ibgateway://status")
def get_gateway_status() -> str:
    """Get the current status of the IB Gateway connection"""
    return """
    # IB Gateway Status
    
    The IB Gateway MCP Server allows you to connect to Interactive Brokers' API
    and retrieve account information, positions, and execute trades.
    
    ## Available Tools
    
    - **get_portfolio_tool**: Retrieve your current portfolio positions and account summary
    
    ## Connection Parameters
    
    - Default Host: 127.0.0.1
    - Default Port: 4001 (TWS Paper: 7497, TWS Live: 7496)
    - Default Client ID: 100
    
    Make sure your IB Gateway or TWS is running and logged in before using these tools.
    """

if __name__ == "__main__":
    mcp.run()
