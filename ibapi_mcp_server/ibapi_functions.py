from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import os

class IBGatewayClient(EClient, EWrapper):
    """
    IB API Client and Wrapper to fetch account summary and positions.
    """
    def __init__(self):
        EClient.__init__(self, self)
        self.account_summary = {}
        self.positions = []
        self._account_summary_done = threading.Event()
        self._positions_done = threading.Event()
        self._connected = threading.Event()
        self._error = None
        # Add these new attributes for market data
        self.market_data = {}
        self._market_data_done = threading.Event()

    def nextValidId(self, orderId):
        """Callback for receiving the next valid order ID."""
        super().nextValidId(orderId)
        print(f"Connected successfully! Next valid order ID: {orderId}")
        self._connected.set()

    def error(self, reqId, errorCode, errorString, advancedOrderDetails=None):
        """Callback for receiving errors from the API."""
        # The base EWrapper.error method does not accept advancedOrderDetails
        super().error(reqId, errorCode, errorString)
        self._error = (reqId, errorCode, errorString)
        # Set done events on critical errors like connection issues
        if errorCode in [1100, 1101, 1102]: # Connection errors
             self._account_summary_done.set()
             self._positions_done.set()


    # Account Summary Callbacks
    def accountSummary(self, reqId, account, tag, value, currency):
        """Callback for receiving account summary data."""
        super().accountSummary(reqId, account, tag, value, currency)
        if account not in self.account_summary:
            self.account_summary[account] = {}
        self.account_summary[account][tag] = value
        # print(f"Account Summary. ReqId: {reqId}, Account: {account}, Tag: {tag}, Value: {value}, Currency: {currency}")

    def accountSummaryEnd(self, reqId):
        """Callback signaling the end of account summary data."""
        super().accountSummaryEnd(reqId)
        print(f"Account Summary End. ReqId: {reqId}")
        self._account_summary_done.set()


    # Position Callbacks
    def position(self, account, contract, pos, avgCost):
        """Callback for receiving position data."""
        super().position(account, contract, pos, avgCost)
        self.positions.append({
            "account": account,
            "contract": {
                "conId": contract.conId,
                "symbol": contract.symbol,
                "secType": contract.secType,
                "lastTradeDateOrContractMonth": contract.lastTradeDateOrContractMonth,
                "strike": contract.strike,
                "right": contract.right,
                "multiplier": contract.multiplier,
                "exchange": contract.exchange,
                "primaryExchange": contract.primaryExchange,
                "currency": contract.currency,
                "localSymbol": contract.localSymbol,
                "tradingClass": contract.tradingClass
            },
            "pos": pos,
            "avgCost": avgCost
        })
        # print(f"Position. Account: {account}, Symbol: {contract.symbol}, SecType: {contract.secType}, Currency: {contract.currency}, Position: {pos}, AvgCost: {avgCost}")

    def positionEnd(self,):
        """Callback signaling the end of position data."""
        super().positionEnd()
        print("Position End")
        self._positions_done.set()

    def tickPrice(self, reqId, tickType, price, attrib):
        """Callback for receiving price tick data."""
        super().tickPrice(reqId, tickType, price, attrib)
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
        
        # Store bid and ask prices
        # tickType 1 is bid price, tickType 2 is ask price
        if tickType == 1:  # Bid
            self.market_data[reqId]['bid'] = price
        elif tickType == 2:  # Ask
            self.market_data[reqId]['ask'] = price
        
        # If we have both bid and ask, we can calculate mid price
        if 'bid' in self.market_data[reqId] and 'ask' in self.market_data[reqId]:
            self.market_data[reqId]['mid'] = (self.market_data[reqId]['bid'] + self.market_data[reqId]['ask']) / 2
            self._market_data_done.set()


def check_gateway_connection(host="127.0.0.1", port=4001, clientId=999):
    """
    Checks if the IB Gateway/TWS is running and can be connected to.
    
    Args:
        host (str): The host address of the IB Gateway/TWS.
        port (int): The port of the IB Gateway/TWS.
        clientId (int): The client ID to use for the connection.
        
    Returns:
        dict: A dictionary containing connection status information:
              - connected (bool): Whether the connection was successful
              - message (str): A descriptive message about the connection status
              - error (str, optional): Error message if connection failed
    """
    import os
    
    # Use provided parameters or fall back to environment variables
    host = host or os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
    port = port or int(os.getenv("IB_GATEWAY_PORT", "4001"))
    clientId = clientId or int(os.getenv("IB_GATEWAY_CLIENT_ID", "999"))
    
    client = IBGatewayClient()
    
    try:
        print(f"Checking connection to {host}:{port} with client ID {clientId}...")
        client.connect(host, port, clientId)
        
        # Start the client in a separate thread
        api_thread = threading.Thread(target=client.run)
        api_thread.start()
        
        # Wait for connection to be established
        connection_successful = client._connected.wait(timeout=5)
        
        # Get error if any
        error_info = client._error
        
        # Disconnect after checking
        client.disconnect()
        api_thread.join()
        
        if connection_successful:
            return {
                "connected": True,
                "message": "Successfully connected to IB Gateway/TWS",
                "host": host,
                "port": port
            }
        else:
            error_msg = f"Error: {error_info[2]} (Code: {error_info[1]})" if error_info else "Connection timed out"
            return {
                "connected": False,
                "message": "Failed to connect to IB Gateway/TWS",
                "error": error_msg,
                "host": host,
                "port": port
            }
    except Exception as e:
        return {
            "connected": False,
            "message": "Exception occurred while connecting to IB Gateway/TWS",
            "error": str(e),
            "host": host,
            "port": port
        }

def get_mid_price(symbol, host="127.0.0.1", port=4001, clientId=102):
    """
    Gets the mid price for a given symbol from IB API.
    
    Args:
        symbol (str): The symbol to get the mid price for.
        host (str): The host address of the IB Gateway/TWS.
        port (int): The port of the IB Gateway/TWS.
        clientId (int): The client ID to use for the connection.
        
    Returns:
        dict: A dictionary containing:
              - symbol (str): The requested symbol
              - mid_price (float): The mid price (average of bid and ask)
              - bid (float): The bid price
              - ask (float): The ask price
              - error (str, optional): Error message if request failed
    """
    import os
    
    # Use provided parameters or fall back to environment variables
    host = host or os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
    port = port or int(os.getenv("IB_GATEWAY_PORT", "4001"))
    clientId = clientId or int(os.getenv("IB_GATEWAY_CLIENT_ID", "102"))
    
    client = IBGatewayClient()
    
    try:
        print(f"Connecting to {host}:{port} with client ID {clientId} to get mid price for {symbol}...")
        client.connect(host, port, clientId)
        
        # Start the client in a separate thread
        api_thread = threading.Thread(target=client.run)
        api_thread.start()
        
        # Wait for connection to be established
        if not client._connected.wait(timeout=10):
            print("Connection timed out or failed.")
            client.disconnect()
            api_thread.join()
            return {"symbol": symbol, "error": "Connection timed out or failed"}
        
        # Create a contract for the symbol
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"  # Default to stock
        contract.currency = "USD"  # Default to USD
        contract.exchange = "SMART"  # Use SMART routing
        
        # Request market data
        req_id = 1001  # Use a unique request ID
        client.reqMktData(req_id, contract, "", False, False, [])
        
        # Wait for market data to be received
        market_data_received = client._market_data_done.wait(timeout=10)
        
        # Cancel market data subscription
        client.cancelMktData(req_id)
        
        # Disconnect
        client.disconnect()
        api_thread.join()
        
        if market_data_received and req_id in client.market_data:
            data = client.market_data[req_id]
            return {
                "symbol": symbol,
                "mid_price": data.get('mid'),
                "bid": data.get('bid'),
                "ask": data.get('ask')
            }
        else:
            return {
                "symbol": symbol,
                "error": "Failed to receive market data"
            }
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e)
        }

def get_portfolio(host="127.0.0.1", port=4001, clientId=100):
    """
    Queries the IB API to get portfolio details (account summary and positions).

    Args:
        host (str): The host address of the IB Gateway/TWS.
        port (int): The port of the IB Gateway/TWS.
        clientId (int): The client ID to use for the connection.

    Returns:
        tuple: A tuple containing two dictionaries:
               - account_summary (dict): Dictionary where keys are account names
                 and values are dictionaries of tag-value pairs.
               - positions (list): A list of dictionaries, each representing a position.
               Returns empty dictionaries/lists on connection or data retrieval failure.
    """
    import os
    
    # Use provided parameters or fall back to environment variables
    host = host or os.getenv("IB_GATEWAY_HOST", "127.0.0.1")
    port = port or int(os.getenv("IB_GATEWAY_PORT", "4001"))
    clientId = clientId or int(os.getenv("IB_GATEWAY_CLIENT_ID", "100"))
    
    client = IBGatewayClient()

    print(f"Connecting to {host}:{port} with client ID {clientId}...")
    client.connect(host, port, clientId)

    # Start the client in a separate thread so the main thread can wait
    api_thread = threading.Thread(target=client.run)
    api_thread.start()

    # Wait for connection to be established
    if not client._connected.wait(timeout=10):
        print("Connection timed out or failed.")
        client.disconnect()
        api_thread.join()
        return {}, [] # Return empty data on connection failure

    # Request data
    # Use unique reqIds for different requests
    account_summary_req_id = 9001 # Choose a unique ID
    client.reqAccountSummary(account_summary_req_id, "All", "$LEDGER") # Request all accounts, $LEDGER tag

    # Positions request does not require a reqId
    client.reqPositions() # Request positions for all accounts

    # Wait for both requests to complete or timeout
    wait_timeout = 30 # seconds
    print("Waiting for account summary and positions data...")

    # Wait for both events to be set
    account_summary_done = client._account_summary_done.wait(timeout=wait_timeout)
    positions_done = client._positions_done.wait(timeout=wait_timeout)

    if not account_summary_done:
        print("Account summary request timed out or failed.")
    if not positions_done:
        print("Positions request timed out or failed.")

    # Disconnect after receiving data or timeout
    client.disconnect()
    api_thread.join() # Wait for the API thread to finish

    print("Disconnected.")

    # Return collected data
    return client.account_summary, client.positions
