from web3 import Web3
from ABIs.ABI import *
import time
class Assets:
    def __init__(self):
        self.list: dict = {}
        self.web3 = Web3(Web3.HTTPProvider('https://evm-rpc-testnet.sei-apis.com'))

    def add_asset(self, name: str, address: str, pool: str):
        # Überprüfe, ob der Name bereits in der Liste existiert
        if name not in self.list:
            # Wenn der Name noch nicht existiert, füge einen neuen Eintrag mit Adresse und Pool hinzu
            contract = self.web3.eth.contract(Web3.to_checksum_address(address),
                                       abi=TOKEN_ABI)
            decimal = contract.functions.decimals().call()
            if not pool:
                lm_pool = ""
                token0 = ""
                token1 = ""
            else:
                lm_pool = self.web3.eth.contract(Web3.to_checksum_address(pool),
                                                         abi=SWAP_PAIR_ABI)
                token0_add=lm_pool.functions.token0().call()
                token1_add=lm_pool.functions.token1().call()
                if token0_add == address:
                    token0 = name
                    token1 = "USD"
                else:
                    token0 = "USD"
                    token1 = name

            self.list[name] = {"address": address, "price": 0, "pool": pool, "decimal": decimal, "token0": token0, "token1": token1}

    def show_assets(self):
        print(self.list)

    def show_asset(self, name: str):
        print(self.list.get(name, "Asset nicht vorhanden"))

    def request_price(self, name: str):
        try:
            if name in self.list:
                lm_pool = self.web3.eth.contract(Web3.to_checksum_address(self.list[name]["pool"]),
                                                         abi=SWAP_PAIR_ABI)
                if self.list[name]["token0"] == "USD":
                    res0=lm_pool.functions.getReserves().call()[0]/10**self.list["USD"]["decimal"]
                    res1 = lm_pool.functions.getReserves().call()[1]/10**self.list[name]["decimal"]
                    self.list[name]["price"] = res0/res1
                else:
                    res0 = lm_pool.functions.getReserves().call()[0] / 10 ** self.list[name]["decimal"]
                    res1 = lm_pool.functions.getReserves().call()[1] / 10 ** self.list["USD"]["decimal"]
                    self.list[name]["price"] = res1 / res0
        except Exception as e:
            print(e)
            time.sleep(0.5)

    def get_liquidity(self, name: str):
        try:
            if name in self.list:
                lm_pool = self.web3.eth.contract(Web3.to_checksum_address(self.list[name]["pool"]),
                                                         abi=SWAP_PAIR_ABI)
                if self.list[name]["token0"] == "USD":
                    res0=lm_pool.functions.getReserves().call()[0]/10**self.list["USD"]["decimal"]
                    res1 = lm_pool.functions.getReserves().call()[1]/10**self.list[name]["decimal"]
                else:
                    res0 = lm_pool.functions.getReserves().call()[0] / 10 ** self.list[name]["decimal"]
                    res1 = lm_pool.functions.getReserves().call()[1] / 10 ** self.list["USD"]["decimal"]
            return res0,res1
        except Exception as e:
            print(e)
            time.sleep(0.5)

    def get_price(self, name: str):
        return self.list[name]["price"]

    def get_prices(self, tickers):
        for name in tickers:
            self.request_price(name)
