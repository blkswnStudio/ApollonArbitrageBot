import time
import requests
import threading


class YFinance:
    URL_BASE: str = 'https://query2.finance.yahoo.com'
    HEADERS = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
    }

    def __init__(self, timeout: int = 5):
        self._credentials = YFinance.request_credentials(timeout)
        self.prices: dict = {}

    def start(self, update_time: float = 1) -> None:
        thread = threading.Thread(target=self._update_loop, args=(update_time,))
        thread.start()

    def get_price(self, symbol: str):
        data = self.prices.get(symbol)
        if not data:
            data = self.request_price(symbol)
            self.prices[symbol] = data
        return data

    def update(self) -> None:
        for symbol in self.prices:
            self.prices[symbol] = self.request_price(symbol)

    def _update_loop(self, update_time: float):
        while True:
            self.update()
            time.sleep(update_time)

    @staticmethod
    def request_credentials(timeout: int, cookieUrl: str = 'https://fc.yahoo.com',
                            crumbUrl: str = '/v1/test/getcrumb') -> dict:
        """
        Requests cookie and crumb from yahoo and returns them.
        """
        cookie = requests.get(cookieUrl).cookies
        crumb = requests.get(url=YFinance.URL_BASE + crumbUrl, cookies=cookie, headers=YFinance.HEADERS, timeout=timeout).text
        return {'cookie': cookie, 'crumb': crumb}

    @staticmethod
    def request_quote(symbols: [str], credentials: {}, timeout: int) -> list[dict]:
        """
        Returns information about provides symbols with the use of credentials (cookie, crumb).
        """
        url = YFinance.URL_BASE + '/v7/finance/quote'
        params = {'symbols': ','.join(symbols), 'crumb': credentials['crumb']}
        response = requests.get(url, params=params, cookies=credentials['cookie'], headers=YFinance.HEADERS,
                                timeout=timeout)
        quotes = response.json()['quoteResponse']['result']
        return quotes

    def request_price(self, symbol: str, timeout: int = 5) -> dict:
        """
        Returns float price of requested symbol.
        """
        try:
            quotes = YFinance.request_quote([symbol], self._credentials, timeout)
            currency = quotes[0].get("currency")
            price = quotes[0].get("regularMarketPrice")
            average_50_days = quotes[0].get("fiftyDayAverage")
            return {"price": price, "currency": currency, "50_days_average": average_50_days}
        except Exception as e:
            return {}


if __name__ == "__main__":
    yf = YFinance()
    yf.start()
    while True:
        p = yf.get_price("EURUSD=X")
        time.sleep(1)