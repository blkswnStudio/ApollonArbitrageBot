
from oracles import Pyth, YFinance


if __name__ == "__main__":
    py = Pyth()
    py.start()
    yf = YFinance()
    print(py.get_price("TSLA"))
    print(yf.get_price("EURUSD=X"))