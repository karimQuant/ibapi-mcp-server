import pytest
from ibapi_mcp_server.ibapi_functions import get_portfolio, get_mid_price
# Define connection parameters for the integration test.
# Ensure your IB Gateway/TWS is running and configured to accept connections
# on this host and port with a unique client ID (e.g., 101).
# It's highly recommended to use environment variables for production
# or sensitive information.
TEST_HOST = "127.0.0.1"
TEST_PORT = 4001 # Or 7497 for paper, 7496 for live
TEST_CLIENT_ID = 101 # Use a different client ID than the main script

# Mark this test to be skipped if the --integration flag is not used with pytest
# This prevents the test from running during standard unit test runs
@pytest.mark.integration
def test_get_portfolio_integration():
    """
    Integration test for get_portfolio function.
    Requires a running IB Gateway/TWS instance accessible at TEST_HOST:TEST_PORT.
    """
    print("\nRunning integration test for get_portfolio...")
    print(f"Attempting to connect to {TEST_HOST}:{TEST_PORT} with client ID {TEST_CLIENT_ID}")

    try:
        account_summary, positions = get_portfolio(TEST_HOST, TEST_PORT, TEST_CLIENT_ID)

        # Basic assertions to check if data was retrieved and is of the expected type.
        # More specific assertions can be added here if you expect certain data
        # (e.g., assert len(account_summary) > 0 if you expect at least one account).
        assert isinstance(account_summary, dict)
        assert isinstance(positions, list)

        print("Integration test completed successfully (basic type check).")
        if account_summary:
            print(f"Received account summary for {len(account_summary)} account(s).")
        if positions:
            print(f"Received {len(positions)} position(s).")
        if not account_summary and not positions:
             print("Warning: No account summary or positions data received. Ensure IB Gateway/TWS is running and connected.")


    except Exception as e:
        # If any exception occurs during the test, fail the test with the exception message
        pytest.fail(f"Integration test failed: {e}")

# To run this test, you will typically use pytest with the --integration flag:
# pytest -m integration
# Ensure you have pytest installed (`pip install pytest`) and your IB Gateway/TWS is running.

@pytest.mark.integration
def test_get_mid_price_integration():
    """
    Integration test for get_mid_price function.
    Requires a running IB Gateway/TWS instance accessible at TEST_HOST:TEST_PORT.
    """
    print("\nRunning integration test for get_mid_price...")
    print(f"Attempting to connect to {TEST_HOST}:{TEST_PORT} with client ID {TEST_CLIENT_ID}")

    # Test with a liquid stock that's likely to have market data available
    symbol = "AAPL"
    
    try:
        result = get_mid_price(symbol, TEST_HOST, TEST_PORT, TEST_CLIENT_ID)

        # Basic assertions to check if data was retrieved and is of the expected type
        assert isinstance(result, dict)
        assert "symbol" in result
        assert result["symbol"] == symbol

        print("Integration test completed successfully (basic type check).")
        
        if "error" in result:
            print(f"Warning: Error received: {result['error']}")
        else:
            print(f"Received mid price for {symbol}: {result.get('mid_price')}")
            print(f"Bid: {result.get('bid')}, Ask: {result.get('ask')}")
            
            # Additional assertions if we have valid data
            assert "mid_price" in result
            assert "bid" in result
            assert "ask" in result
            assert result["ask"] >= result["bid"], "Ask price should be greater than or equal to bid price"

    except Exception as e:
        # If any exception occurs during the test, fail the test with the exception message
        pytest.fail(f"Integration test failed: {e}")
