from ibapi.client import EClient
from ibapi.wrapper import EWrapper

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        
    def nextValidId(self, orderId):
        print(f"Connected successfully! Next valid order ID: {orderId}")
        self.disconnect()

app = TestApp()
# For paper trading use port 7497, for live trading use 7496
app.connect("127.0.0.1", 4001, 100)
app.run()
