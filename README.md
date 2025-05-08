# Interactive Brokers API FastMCP Server

A server implementation for Interactive Brokers' API that allows LLMs to interact with your IB account using the Model Context Protocol (MCP).

## Overview

This project creates a middleware server that connects to Interactive Brokers Gateway and exposes its functionality through the FastMCP framework. This allows LLMs like Claude to interact with your IB account, retrieve portfolio information, and potentially execute trades.

## Features

- Connect to Interactive Brokers Gateway via the official IB API
- Support multiple simultaneous client connections through FastMCP
- Expose IB functionality as MCP tools and resources
- Connection status monitoring
- Error handling and logging

## Prerequisites

- Python 3.11+
- Interactive Brokers Gateway installed and running
- IB account with API access enabled

## Installation

1. Clone this repository:
```
git clone https://github.com/karimQuant/ibapi-mcp-server.git
cd ibapi-mcp-server
```

2. Install dependencies:
```
pip install -e .
```

## Usage

1. Start your IB Gateway and log in
2. Run the server:

   a. Using stdio transport (default):
   ```
   python server.py
   ```
   
   b. Using SSE transport:
   ```
   python server.py sse
   ```
   
   c. Using SSE transport with custom port:
   ```
   python server.py sse port=9000
   ```

   d. Using the FastMCP CLI:
   ```
   fastmcp run server.py
   ```

   e. For development with an interactive testing environment:
   ```
   fastmcp dev server.py
   ```

3. Connect client applications (like Claude Desktop) to the server

## API Documentation

The FastMCP Server provides the following functionality:

### Available Tools

- **get_portfolio_tool**: Retrieve your current portfolio positions and account summary

### Resources

- **ibgateway://{host}/{port}**: Get the current status of the IB Gateway connection

## License

MIT

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
