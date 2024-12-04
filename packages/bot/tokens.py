from web3 import Web3

from packages.bot.w3 import w3
from abi import TOKEN_ABI


class Tokens:

    def __init__(self, token_addresses: list[str] = None) -> None:
        token_addresses: list = [] if not token_addresses else token_addresses
        self.token_addresses = [Web3.to_checksum_address(token_address) for token_address in token_addresses]
        self.tokens: dict = {}
        self._addresses_to_symbols: dict = {}

        for token_address in self.token_addresses:
            self.add_token(token_address)

    """ Handling """
    def add_token(self, token_address: str) -> None:
        token_address: str = Web3.to_checksum_address(token_address)
        contract = w3.eth.contract(address=token_address, abi=TOKEN_ABI)
        symbol: str = contract.functions.symbol().call()
        decimals: int = contract.functions.decimals().call()
        self.tokens[symbol] = {"address": token_address, "contract": contract, "decimals": decimals}
        self._addresses_to_symbols[token_address] = symbol

    """ Getter """
    def get_symbol(self, token_address: str) -> str:
        return self._addresses_to_symbols[token_address]

    def get_decimals(self, symbol: str) -> int:
        return self.tokens[symbol]["decimals"]

    def get_address(self, symbol: str) -> str:
        return self.tokens[symbol]["address"]

    """ Request """

    def request_balance_of(self, symbol: str, address: str) -> float:
        contract = self.tokens[symbol]["contract"]
        return contract.functions.balanceOf(symbol, address) / 10 ** self.get_decimals(symbol)
