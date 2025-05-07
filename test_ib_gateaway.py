from ib_gateway_function import get_portfolio

# For paper trading use port 7497, for live trading use 7496
# Default port 4001 is often used for the Gateway
HOST = "127.0.0.1"
PORT = 4001 # Or 7497 for paper, 7496 for live
CLIENT_ID = 100

if __name__ == "__main__":
    account_summary, positions = get_portfolio(HOST, PORT, CLIENT_ID)

    print("\n--- Account Summary ---")
    if account_summary:
        for account, data in account_summary.items():
            print(f"Account: {account}")
            for tag, value in data.items():
                print(f"  {tag}: {value}")
    else:
        print("No account summary data received.")

    print("\n--- Positions ---")
    if positions:
        for pos in positions:
            contract = pos['contract']
            print(f"  {contract['symbol']} ({contract['secType']}) @ {contract['exchange']}: Pos={pos['pos']}, AvgCost={pos['avgCost']}")
    else:
        print("No positions data received.")
