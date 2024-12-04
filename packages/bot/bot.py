import time
import math
import threading
from web3 import Web3

from packages.bot import tokens
from packages.bot.adapter import TroveFactory
from packages.bot.oracles import pyth, yfinance

from packages.bot.pools import Pools


class Bot:
    TROVE_FACTORY_ADDRESS: str = "0xd055CCEca066144349ed69231129674156CED783"

    POOLS_LST: list = [
        "0xdcaCA0215344c3fc3DAB35e0432319fBF53d53ab",  # AAPL
        "0x2b2c69a9f5677f4169b0A464CB36B9D744c03a81",  # TSLA
        "0xd8Bd5F7acAB978F36c7ae5AF9ebf1388EE9334C9",  # MSTR
        "0x95218d7672f80Ac345c06BbE64Bf0657744e74b8",  # XAG
        "0xFfa2FCf91033E013BAb79548a5B3F151023adEA3"  # NVDA
    ]

    TRIGGER: float = 0.10

    BASE_COLLATERAL_TOKEN: str = "0x5abdaEF2aa41B075B074ABE0711fB1cC6FB09284"

    def __init__(self):
        self.running = False
        self.pools = Pools(self.POOLS_LST)

        self.trove_factory: TroveFactory = TroveFactory(self.TROVE_FACTORY_ADDRESS)
        self.trove_factory.approve_token(self.BASE_COLLATERAL_TOKEN, 999999999999)

    def start(self, update_time: float):
        self.running = True
        yfinance.start(update_time)
        pyth.start(update_time)
        self.pools.start(update_time)

        thread = threading.Thread(target=self._loop)
        thread.start()

    def _loop(self):
        while self.running:
            for pool_symbol, pool_data in self.pools.pools.items():
                pool_price: float = self.pools.get_price(pool_symbol)
                oracle_symbol: str = pool_data["token_1_symbol"][1:]
                oracle_price: float = pyth.get_price(oracle_symbol)

                # Premium
                difference: float = abs(self.pools.get_price(pool_symbol) / oracle_price - 1)
                print(pool_symbol, difference * 100)
                if difference > self.TRIGGER:
                    reserves: dict = self.pools.get_reserves(pool_symbol)
                    # Premium
                    if pool_price > oracle_price:
                        dept_token: str = pool_symbol.split("-")[1]
                        new_collateral_token: str = pool_symbol.split("-")[0]
                        target: float = 1.1 / (1 + difference) * pool_price
                        amount_in: float = (math.sqrt(reserves[new_collateral_token] * reserves[dept_token] / target)
                                            - reserves[dept_token])
                        self.execute(dept_token, amount_in, new_collateral_token)

                    # Discount
                    elif pool_price < oracle_price:
                        dept_token: str = pool_symbol.split("-")[0]
                        new_collateral_token: str = pool_symbol.split("-")[1]
                        target: float = 0.9 / (1 - difference) * pool_price
                        amount_in: float = (math.sqrt(target * reserves[dept_token] * reserves[new_collateral_token]) -
                                            reserves[dept_token])

                        print(target)
                        print(amount_in)
                        self.execute(dept_token, amount_in, new_collateral_token)
            time.sleep(5)

    def execute(self, dept_token_symbol: str, dept_token_amount: float, new_collateral_symbol: str):
        collateral_token_address: str = self.BASE_COLLATERAL_TOKEN
        collateral_token_amount: float = 4000
        dept_token_address: str = tokens.get_address(dept_token_symbol)
        dept_token_amount: float = dept_token_amount
        new_collateral_address: str = tokens.get_address(new_collateral_symbol)

        tx_hash: str = self.trove_factory.execute(collateral_token_address, collateral_token_amount,
                                                  dept_token_address, dept_token_amount, new_collateral_address)

        print(tx_hash)

