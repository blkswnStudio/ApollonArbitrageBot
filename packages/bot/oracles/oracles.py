from abc import ABC, abstractmethod


class Oracles(ABC):

    @abstractmethod
    def start(self, update_time: float = 1) -> None:
        pass

    @abstractmethod
    def get_price(self, symbol: str) -> dict:
        pass

    @abstractmethod
    def update(self) -> None:
        pass
