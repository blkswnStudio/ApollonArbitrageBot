import time
from web3 import Web3

from abi import TROVE_FACTORY_ABI

class TroveFactory:
    EXECUTE_GAS: int = 1500000

    def __init__(self, w3: Web3, trave_factory_address: str):
        self.w3: Web3 = w3
        self.trave_factory_address: str = Web3.to_checksum_address(trave_factory_address)
        self.trave_factory_contract = self.w3.provider.eth.contract(address=self.trave_factory_address, abi=TROVE_FACTORY_ABI)

    def execute(self, collateralTokenAddress: str, collateralAmount: float, 
                deptTokenAddress: str, deptAmount: float,
                newCollateralAddress: str,):
        pass

    def deposit():
        pass

    def withdraw():
        pass


if __name__ == "__main__":
    pass
