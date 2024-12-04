import os

from web3 import Web3
from web3.providers.base import BaseProvider

RPC_URLS: list[str] = str(os.getenv("RPC_URLS")).split(",")


# Init Web3
class Provider(BaseProvider):
    def __init__(self, providers: list[Web3.HTTPProvider]):
        super().__init__()
        self.providers = providers
        self.current_provider = 0

    def make_request(self, method, params):
        for provider in self.providers:
            try:
                return provider.make_request(method, params)
            except Exception as e:
                continue
        raise Exception("All providers failed")


fallback_provider = Provider([Web3.HTTPProvider(rpc) for rpc in RPC_URLS])
w3 = Web3(fallback_provider)
