import time
import requests
import threading

from .oracles import Oracles


class Pyth(Oracles):
    URL_BASE: str = 'https://hermes.pyth.network'

    ORACLE_ID_MAPPING: dict = {
        "BTC": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
        "USDT": "2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b",
        "SEI": "",
        "MSTR": "e1e80251e5f5184f2195008382538e847fafc36f751896889dd3d1b1f6111f09",
        "XAG": "f2fb02c32b055c805e7238d628e5e9dadef274376114eb1f012337cabe93871e",
        "NVDA": "b1073854ed24cbc755dc527418f52b7d271f6cc967bbf8d8129112b18860a593",
        "AAPL": "49f6b65cb1de6b10eaf75e7c03ca029c306d0357e91b5311b175084a5ad55688",
        "TSLA": "16dad506d7db8da01c87581c87ca897a012a153557d4d578c3b9c9e1bc0632f1"
    }
    SYMBOLS_MAPPING: dict = {v: k for k, v in ORACLE_ID_MAPPING.items()}

    def __init__(self, timeout: int = 5):
        self.data: dict = {}

    def start(self, update_time: float = 1) -> None:
        thread = threading.Thread(target=self._update_loop, args=(update_time,))
        thread.start()

    def get_price(self, symbol: str) -> dict:
        price: float = self.data.get(symbol)
        if not price:
            data = self.request_prices([symbol])
            price: float = data["prices"][symbol]
            self.data[symbol] = {"price": price}
        return {"price": price}

    def update(self) -> None:
            data = self.request_prices(list(self.data.keys()))
            for symbol, price in data["prices"].items():
                self.data[symbol] = {"price": price}

    def _update_loop(self, update_time: float):
        while True:
            self.update()
            time.sleep(update_time)

    def request_prices(self, symbols: list[str], fetchBinary: bool = False, timeout: int = 5) -> dict:
        """
        Returns float price of requested symbol.
        """
        oracle_ids: list[str] = [self.ORACLE_ID_MAPPING[symbol] for symbol in symbols if self.ORACLE_ID_MAPPING.get(symbol)]
        ids: str = '&'.join([f"ids%5B%5D={oracle_id}" for oracle_id in oracle_ids])
        url: str = f'{self.URL_BASE + f"/v2/updates/price/latest?{ids}&encoding=hex&parsed=true&ignore_invalid_price_ids=false"}'
        try:
            # Request data
            data = requests.get(url).json()

            # Sort prices 
            prices: dict = {self.SYMBOLS_MAPPING[price_data["id"]]: round(int(price_data["price"]["price"]) * 10 ** int(price_data["price"]["expo"]), 4)  
                                for price_data in data["parsed"]}
            
            # Sort Binary
            binary: bytes = bytes.fromhex(data["binary"]["data"][0])

            result: dict = {"prices": prices}
            if fetchBinary:
                result["binary"] = binary
            return result
        except Exception as e:
            return {"prices": {}}
