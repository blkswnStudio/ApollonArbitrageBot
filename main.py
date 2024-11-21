import time
import threading
from packages.bot.oracles.yfinance import YFinance
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
assets.add_asset("USD", "0xAE34739a521521DE17902999ff8FBb12394192a1", "")
assets.add_asset("AAPL", "0x03991Ef0b2987487B72829b793e418F8757DE376", "0xdcaCA0215344c3fc3DAB35e0432319fBF53d53ab")
assets.add_asset("TSLA", "0x2E5AE8fbE2e5cd9dA8710E1DDebe64A1BA121Ae4", "0x2b2c69a9f5677f4169b0A464CB36B9D744c03a81")
assets.add_asset("MSTR", "0x284352a2E970C7B83Ae069A8de7dd61F4e7f5f7a", "0xd8Bd5F7acAB978F36c7ae5AF9ebf1388EE9334C9")
assets.add_asset("XAG", "0xc01b65f7B86a3D171b8C7f1CE3B437Bd4Ca68093", "0x95218d7672f80Ac345c06BbE64Bf0657744e74b8")
assets.add_asset("NVDA", "0x7938486225755BeC1fc202CA80799d27f108B33f", "0xFfa2FCf91033E013BAb79548a5B3F151023adEA3")

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
        try:
            data[name]["premium"] = data[name]["dex_price"] / data[name]["yf_price"] * 100
        except:
            data[name]["premium"] = 100.0
def run_bot():
    try:
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
                    if time.time() - data[name]["time"] > 60*30:
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
    except Exception as e:
        pass
        print(e)

if __name__ == '__main__':
    # Start der Preisaktualisierung in einem separaten Thread

    thread = threading.Thread(target=update_prices_yf)
    thread.start()

    thread = threading.Thread(target=update_prices_dex)
    thread.start()

    thread = threading.Thread(target=run_bot)
    thread.start()

    bot.data = data
    bot.run()

