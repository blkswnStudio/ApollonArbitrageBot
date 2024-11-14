import time
import threading
from yfinance import YFinance
from assets import Assets
from web3 import Web3
from ABIs.ABI import *
from telegrambot import ApollonTelegramBot
import os
import math
from dotenv import load_dotenv

# Load Telegram
load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')
chat_id = -4505251217
bot = ApollonTelegramBot(token, chat_id)
bot.send_telegram_msg('Setting Up all Parameters')

# Manage Tickers
tickers = ["AAPL", "TSLA", "MSTR", "XAG", "NVDA"]
yf_tickers = ["AAPL", "TSLA", "MSTR", "XAGX-USD", "NVDA"]

data: dict = {ticker: {"dex_price": float(0), "yf_price": float(0), "premium": float(0), "last_premium": float(0), "time": 0, "limit": [0]} for ticker in tickers}

assets = Assets()
assets.add_asset("USD", "0xA2efBedf2a9954aC0854933d148F9B5Df9C1FeE0", "")
assets.add_asset("AAPL", "0x5978a4fEe819ddbf2195a3671e73D18F9Dae7ae7", "0xe9BF367408567CdE44ca83548e596748e997b2EB")
assets.add_asset("TSLA", "0x895D225434b4c889eAd8Bc30aFF8c770Eefc177D", "0x73d8739b61A7BFD613d96aB8A6EDd03394D2f965")
assets.add_asset("MSTR", "0x10D2c0522D5852Ba2eEc51542036bEC7E01b418a", "0x58fdbf9416F385E2Fa737ab1059bD3940b7443bD")
assets.add_asset("XAG", "0xA8Cc0b87B8f91Fa4070F67a89bc2DB3ab4c94F62", "0x1b620Da7d7c63b9D2bCB1549BEd1f4aae542d85B")
assets.add_asset("NVDA", "0x0E4a80556B98fF991D6700BBe5A99f51D224623d", "0x0eA63793856fDeE52F9EB49547BD39724b4E9560")

yf = YFinance()
yf.start()

def update_prices_yf():
    while True:
        for name in data:
            yf_name = name
            if name == "XAG":
                yf_name = "XAGX-USD"
            yf_price = yf.get_price(yf_name)
            data[name]["yf_price"] = yf_price["price"]

def update_prices_dex():
    while True:
        assets.get_prices(tickers)
        time.sleep(1)

def all_prices_updated():
    for ticker in tickers:
        if data[ticker]["yf_price"] == 0 or data[ticker]["yf_price"] == None:
            return False
    return True

def calc_volume(name: str):
    A,B=assets.get_liquidity(name)
    print(data[name]["premium"])
    if data[name]["premium"] < 90:
        tokenin='USD'
        tokenout= name
        price = data[name]["dex_price"]
        target = 90 / data[name]["premium"] * data[name]["dex_price"]
        amountin= math.sqrt(target*A*B)-A
    if data[name]["premium"] > 110:
        tokenin=name
        tokenout='USD'
        price = data[name]["dex_price"]
        target = 110 / data[name]["premium"] * data[name]["dex_price"]
        amountin= math.sqrt(A*B/target)-B
    return amountin

def send_update():
    message = "Time: " + f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
    message += "Asset, Oracle/Dex, Premium\n"
    for name in data:
        message += f"{name}, {data[name]['dex_price']:.2f} jUSD / {data[name]['yf_price']:.2f} $, {data[name]['premium']:.2f} %\n"#
    print(message)
    bot.send_telegram_msg(message)

def update_dex_premium():
    for name in data:
        data[name]["dex_price"] = assets.list[name]["price"]
    for name in data:
        data[name]["premium"] = data[name]["dex_price"] / data[name]["yf_price"] * 100
def run_bot():
    t0=time.time()
    while True:
        if all_prices_updated():
            break
        else:
            print(data)
            time.sleep(1)
    bot.send_telegram_msg('Setup was successfull. Wait 5s to iterate trough all data.')
    time.sleep(5)
    update_dex_premium()
    send_update()
    while True:
        update_dex_premium()
        if time.time()-t0 >=60*60:
            send_update()
            t0 = time.time()
        for name in data:
            premium_value = data[name]["premium"]
            #print(premium_value)
            if abs(premium_value - 100) > 10.0 and premium_value != 0:
                if time.time() - data[name]["time"] > 60:
                    amountin = calc_volume(name)
                    data[name]["time"] = time.time()
                    message = "Asset, Oracle/Dex, Premium\n"
                    message += f"{name}, {data[name]['dex_price']:.2f} jUSD / {data[name]['yf_price']:.2f} $, {data[name]['premium']:.2f} %\n"
                    if premium_value - 100 < 0.0:
                        message += f"Swappe {amountin:.2f} jUSD gegen {name} damit Ratio bei 90 %\n"
                        bot.send_telegram_msg(message)
                    if premium_value - 100 > 0.0:
                        message += f"Swappe {amountin:.2f} {name} gegen jUSD damit Ratio bei 110 %\n"
                        bot.send_telegram_msg(message)
        for name in data:
            if abs(data[name]["premium"] - 100) < 10.0 and abs(data[name]["last_premium"] - 100) > 10 or abs(
                    data[name]["premium"] - 100) > 10.0 and abs(data[name]["last_premium"] - 100) < 10:
                if (data[name]["premium"] != 0 and data[name]["last_premium"] != 0):
                    message = f"Premium Changed for {name}\n"
                    message += f"Old: {data[name]['last_premium']:.2f} %, New: {data[name]['premium']:.2f} %\n"
                    bot.send_telegram_msg(message)
        for name in data:
            data[name]["last_premium"] = data[name]["premium"]

        time.sleep(1)

if __name__ == '__main__':
    # Start der Preisaktualisierung in einem separaten Thread

    thread = threading.Thread(target=update_prices_yf)
    thread.start()

    thread = threading.Thread(target=update_prices_dex)
    thread.start()

    thread = threading.Thread(target=run_bot)
    thread.start()

    bot.run()

