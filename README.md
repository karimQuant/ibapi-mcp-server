# Interactive Brokers API Multi-Client Protocol Server

A server implementation for Interactive Brokers' Client Portal API that allows multiple clients to connect simultaneously.

## Overview

This project creates a middleware server that connects to Interactive Brokers' Client Portal API and allows multiple client applications to connect to it simultaneously. The server handles authentication, session management, and request proxying to IB's API.

## Features

- Connect to Interactive Brokers Gateway via REST API
- Support multiple simultaneous client connections
- Simple authentication system
- Request routing and response handling
- Connection status monitoring
- Error handling and logging

## Prerequisites

- Python 3.8+
- Interactive Brokers Gateway installed and running
- IB account with Client Portal API access enabled

## Installation

1. Clone this repository:
```
git clone https://github.com/karimQuant/ibapi-mcp-server.git
cd ibapi-mcp-server
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure your settings in `config.py`

## Usage

1. Start your IB Gateway and log in
2. Run the server:
```
python server.py
```
3. Connect client applications to `http://localhost:8080` (default)

## API Documentation

The MCP (Multi-Client Protocol) Server provides the following functionality:

### Available Tools

- **get_portfolio**: Retrieve your current portfolio positions and values
- **get_trades**: Access your recent trade history and execution details
- **get_instrument_price**: Get real-time or delayed pricing for financial instruments
- **get_instrument_info**: Retrieve detailed information about specific financial instruments

### Endpoints

Details on how to use these endpoints will be added soon.

## License

MIT

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
