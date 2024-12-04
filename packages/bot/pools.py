import threading
import time

from web3 import Web3

from abi import SWAP_PAIR_ABI

from packages.bot import tokens
from packages.bot.w3 import w3

from packages.bot.utils import calc_out_given_in, calc_in_given_out


class Pools:

    def __init__(self, pool_addresses: list[str] = None) -> None:
        pool_addresses: list = [] if not pool_addresses else pool_addresses

        self.pool_addresses = [Web3.to_checksum_address(pool_address) for pool_address in pool_addresses]
        self.pools: dict = {}
        self._addresses_to_symbols: dict = {}

        for pool_address in self.pool_addresses:
            self.add_pool(pool_address)

    """ Handler """

    def add_pool(self, pool_address: str) -> None:
        pool_address: str = Web3.to_checksum_address(pool_address)
        contract = w3.eth.contract(address=pool_address, abi=SWAP_PAIR_ABI)

        # Symbol
        token0_address: str = contract.functions.token0().call()
        token1_address: str = contract.functions.token1().call()
        tokens.add_token(token0_address)
        tokens.add_token(token1_address)
        token_0_symbol: str = tokens.get_symbol(token0_address)
        token_1_symbol: str = tokens.get_symbol(token1_address)
        symbol: str = "-".join((token_0_symbol, token_1_symbol))

        # Decimals
        decimals: int = contract.functions.decimals().call()

        self.pools[symbol] = {"address": pool_address, "contract": contract, "decimals": decimals,
                              "token_0_symbol": token_0_symbol, "token_1_symbol": token_1_symbol}
        self._addresses_to_symbols[pool_address] = symbol

        # Using internal methods
        reserves: dict = self.request_reserves(symbol)
        self.pools[symbol]["reserves"] = reserves

    def start(self, update_time: float = 1) -> None:
        thread = threading.Thread(target=self._update_loop, args=(update_time,))
        thread.start()

    def update(self) -> None:
        for pool_symbol in self.pools:
            reserves: dict = self.request_reserves(pool_symbol)
            self.pools[pool_symbol]["reserves"] = reserves

    def _update_loop(self, update_time: float) -> None:
        while True:
            self.update()
            time.sleep(update_time)

    """ Getter """

    def get_symbol(self, token_address: str) -> str:
        return self._addresses_to_symbols[token_address]

    def get_address(self, symbol: str) -> str:
        return self.pools[symbol]["address"]

    def get_reserves(self, symbol: str) -> dict:
        return self.pools[symbol]["reserves"]

    def get_price(self, symbol) -> float:
        reserves: list = list(self.get_reserves(symbol).values())
        return reserves[0] / reserves[1]

    """ Request """

    def request_reserves(self, pool_symbol: str) -> dict:
        contract = self.pools[pool_symbol]["contract"]
        token_0_symbol: str = self.pools[pool_symbol]["token_0_symbol"]
        token_1_symbol: str = self.pools[pool_symbol]["token_1_symbol"]
        reserves: list = contract.functions.getReserves().call()
        token0_reserve: float = float(reserves[0] / 10 ** tokens.get_decimals(token_0_symbol))
        token1_reserve: float = float(reserves[1] / 10 ** tokens.get_decimals(token_1_symbol))
        return {token_0_symbol: token0_reserve, token_1_symbol: token1_reserve}

    def request_swap_fee(self, pool_symbol: str, token_in: str, amount_in: float) -> float:
        amount_out: float = - self.get_amount_out(pool_symbol, token_in, amount_in, swap_fee=0)
        contract = self.pools[pool_symbol]["contract"]
        token_0_symbol: str = self.pools[pool_symbol]["token_0_symbol"]
        token_1_symbol: str = self.pools[pool_symbol]["token_1_symbol"]
        reserves: list = list(self.get_reserves(pool_symbol).values())
        post_0_reserve: int = int(((reserves[0] + (amount_in if token_in == token_0_symbol else amount_out))
                                   * 10 ** tokens.get_decimals(token_0_symbol)))
        post_1_reserve: int = int(((reserves[1] + (amount_out if token_in == token_0_symbol else amount_in))
                                   * 10 ** tokens.get_decimals(token_1_symbol)))
        return contract.functions.getSwapFee(post_0_reserve, post_1_reserve).call()[0] / 10 ** 18

    """ Calculation """

    def get_amount_out(self, pool_symbol: str, token_in: str, amount_in: float, swap_fee: float = 0.003) -> float:
        token_0_symbol: str = self.pools[pool_symbol]["token_0_symbol"]
        token_1_symbol: str = self.pools[pool_symbol]["token_1_symbol"]
        token_out: str = token_0_symbol if token_in == token_1_symbol else token_1_symbol
        reserves: dict = self.get_reserves(pool_symbol)
        return calc_out_given_in(amount_in, reserves[token_in], reserves[token_out],
                                 0.5, 0.5, swap_fee)

    def get_amount_in(self, pool_symbol: str, token_out: str, amount_out: float, swap_fee: float = 0.003) -> float:
        token_0_symbol: str = self.pools[pool_symbol]["token_0_symbol"]
        token_1_symbol: str = self.pools[pool_symbol]["token_1_symbol"]
        token_in: str = token_0_symbol if token_out == token_1_symbol else token_1_symbol
        reserves: dict = self.get_reserves(pool_symbol)
        return calc_in_given_out(amount_out, reserves[token_in], reserves[token_out],
                                 0.5, 0.5, swap_fee)
