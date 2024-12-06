import time
import requests
import threading
from web3 import Web3
from .oracles import Oracles
from ABIs.ABI import *


class JAssets(Oracles):

    def __init__(self, assets, timeout: int = 5):
        self.data = {}
        # Iterate over the items in assets.list
        for key, value in assets.list.items():
            if key != "USD":  # Check if the key is not 'USD'
                # Initialize self.data[key] as a dictionary
                self.data[key] = {}
                # Set the 'address' key in the dictionary to the value's 'address'
                self.data[key] = {
                    "address": value.get('address'),  # Set the 'address' field
                    "price": 0,  # Initialize 'price' to 0
                    "pyth": True  # Initialize 'pyth' to True
                }
        self.web3 = Web3(Web3.HTTPProvider('https://evm-rpc-testnet.sei-apis.com'))
        self.pricefeed_contract = self.web3.eth.contract(Web3.to_checksum_address('0x2eA326623a323940BcA88bdA24dDc2e8D657749c'),
                                               abi=PRICEFEED_ABI)
    def start(self, update_time: float = 1) -> None:
        thread = threading.Thread(target=self._update_loop, args=(update_time,))
        thread.start()

    def get_price(self, symbol: str):
        return self.data[symbol]

    def update(self) -> None:
        for symbol in self.data:
            back_=self.request_price(symbol)
            self.data[symbol]['price'] = back_[0]
            self.data[symbol]['pyth'] = back_[1]

    def _update_loop(self, update_time: float):
        while True:
            self.update()
            time.sleep(update_time)

    def request_price(self, symbol: str, timeout: int = 5) -> dict:
        try:
            return self.pricefeed_contract.functions.getPrice(self.data[symbol]["address"]).call()[0]/1e18, self.pricefeed_contract.functions.getPrice(self.data[symbol]["address"]).call()[1]
        except Exception as e:
            return {}

if __name__ == "__main__":
    jassets = JAssets()
    # Example: Add initial data to track BTC
    jassets.data = {"BTC": {"price": 0}}
