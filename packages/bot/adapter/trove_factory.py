import time
import os
from web3 import Web3

from .abi import TOKEN_ABI, TROVE_FACTORY_ABI
from .utils import float_to_int

from oracles import Pyth


class TroveFactory:
    EXECUTE_GAS: int = 10000000

    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY")
    ADDRESS = Web3().eth.account.from_key(PRIVATE_KEY).address

    DON_UPDATE_PRICE: list[str] = ["SEI"]
    DONT_UPDATE_PRICE: list[str] = ["jUSD", "JLY"]

    def __init__(self, w3: Web3, trave_factory_address: str):
        self.w3: Web3 = w3
        self.pyth = Pyth()
        self.trave_factory_address: str = Web3.to_checksum_address(trave_factory_address)
        self.trave_factory_contract = self.w3.eth.contract(address=self.trave_factory_address, abi=TROVE_FACTORY_ABI)

        self.dept_symbols: list[str] = [self.get_token_symbol(token_address) for token_address in self.get_dept_token_addresses()]
        self.coll_symbols: list[str] = [self.get_token_symbol(token_address) for token_address in self.get_call_token_addresses()]
        self.update_prices_symbols: set[str] = set([(symbol[1:] if symbol[:1] == "j" else symbol)
                                                    for symbol in self.dept_symbols + self.coll_symbols
                                                    if symbol not in self.DONT_UPDATE_PRICE])

    def get_dept_token_addresses(self) -> list[str]:
        return self.trave_factory_contract.functions.getDebtTokenAddresses().call()

    def get_call_token_addresses(self) -> list[str]:
        return self.trave_factory_contract.functions.getCollTokenAddresses().call()

    def execute(self, collateral_token_address: str, collateral_amount: float, 
                dept_token_address: str, dept_amount: float,
                new_collateral_address: str) -> str:
        
        collateral_token_contract = self.w3.eth.contract(address=collateral_token_address, abi=TOKEN_ABI)
        collateral_token_decimals: int = collateral_token_contract.functions.decimals().call()

        dept_token_contract = self.w3.eth.contract(address=dept_token_address, abi=TOKEN_ABI)
        dept_token_decimals: int = dept_token_contract.functions.decimals().call()

        collateral_token_amount: int = float_to_int(collateral_amount, collateral_token_decimals)
        dept_token_amount: int = float_to_int(dept_amount, dept_token_decimals)

        # Create the tuples for collateral and debt parameters
        collateral_tuple = (collateral_token_address, collateral_token_amount)
        debt_tuple = (dept_token_address, dept_token_amount)
        
        # Fetch price bytes
        prices_bytes: bytes = self.get_update_prices_bytes(list(self.update_prices_symbols))

        txn = self.trave_factory_contract.functions.execute(
            collateral_tuple,
            debt_tuple,
            new_collateral_address,
            [prices_bytes]
        )

        tx = txn.build_transaction({
            "chainId": self.w3.eth.chain_id,
            "gas": self.EXECUTE_GAS,
            "gasPrice": int(self.w3.eth.gas_price * 1.1),  # 10% extra fee
            'nonce': self.w3.eth.get_transaction_count(self.ADDRESS),
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.PRIVATE_KEY)
        tx_hash: str = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction).hex()
        return "0x" + tx_hash if tx_hash[:2] != "0x" else tx_hash

    def deposit(self):
        pass

    def withdraw(self):
        pass

    def approve_token(self, token_address: str, amount: float) -> str:
        token_contract = self.w3.eth.contract(address=token_address, abi=TOKEN_ABI)
        token_decimals: int = token_contract.functions.decimals().call()

        txn = token_contract.functions.approve(
            self.trave_factory_address,
            float_to_int(amount, token_decimals)
        )

        tx = txn.build_transaction({
            "chainId": self.w3.eth.chain_id,
            "gas": self.EXECUTE_GAS,
            "gasPrice": int(self.w3.eth.gas_price * 1.1),  # 10% extra fee
            'nonce': self.w3.eth.get_transaction_count(self.ADDRESS),
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.PRIVATE_KEY)
        tx_hash: str = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction).hex()
        return "0x" + tx_hash if tx_hash[:2] != "0x" else tx_hash
    
    def get_token_symbol(self, token_address: str) -> str:
        token = self.w3.eth.contract(address=token_address, abi=TOKEN_ABI)
        return token.functions.symbol.call()
    
    def get_update_prices_bytes(self, symbols: list[str]) -> bytes:
        return self.pyth.request_prices(symbols, True)["binary"]
    
