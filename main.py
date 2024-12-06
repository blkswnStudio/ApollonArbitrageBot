import time
import threading
from packages.bot.oracles.yfinance import YFinance
from packages.bot.oracles.pyth import Pyth
from assets import Assets
from redeem_assets import Redeem_Assets
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
redeemers = ["USDT"]

data: dict = {ticker: {"dex_price": float(0), "yf_price": float(0), "jasset_oracle": float(0), "jasset_isPyth": True, "premium": float(0), "last_premium": float(0), "time": 0, "limit": [0]} for ticker in tickers}
data_redeem: dict = {ticker: {"dex_price": float(0), "premium": float(0), "last_premium": float(0), "time": 0, "limit": [0]} for ticker in redeemers}

assets = Assets()
assets.add_asset("USD", "0x927be311030529D3Cc5AEcE1Fc2417DB14CCaf99", "")
assets.add_asset("AAPL", "0x46ADE58267Fe168578Bb46A4Cc247951D0Ea48CF", "0xbf597d4918649D9D458AD39372859d7924831Cdf")
assets.add_asset("TSLA", "0xBD80DC04c68155Fdee2741634199703870B7A969", "0xff4DbA6Cd61bD2d6770A8D4074C947807A64BFeB")
assets.add_asset("MSTR", "0xEd09eF091A3e41174a744A774E00d1D1b70B20A6", "0x8Ba635330329D230ADC5E9049cF5475c7A65b765")
assets.add_asset("XAG", "0xeB7DE5Cb7f0E0b110C93Dc100eCe9710AD511F6c", "0xeB6618941A1E218fBa7B2EC0ead6D5a703DB58ea")
assets.add_asset("NVDA", "0x8b2851539892892F848Bb6620145E5f90F13a948", "0xA095548d0A5Ed34dF624a2344bC63CE47bE7B47b")

redeem_assets = Redeem_Assets()
redeem_assets.add_asset("USD", "0x927be311030529D3Cc5AEcE1Fc2417DB14CCaf99", "")
redeem_assets.add_asset("USDT", "0x92D2CaDF5C34D70ddf5884a5730430fbE146EC24", "0x086B0bfc1F2C17d2f6c9FC8478c361916a93c057")
redeem_assets.request_price("USDT")
print(1/redeem_assets.get_price("USDT"))

yf = YFinance()
yf.start()

pyth = Pyth()
pyth.start()

# True:
#    print(pyth.get_price('MSTR'))
#    print(pyth.get_price('AAPL'))
#    time.sleep(2)

def update_prices_yf():
    while True:
        for name in data:
            try:
                yf_name = name
                if name == "XAG":
                    yf_name = "XAGX-USD"
                yf_price = yf.get_price(yf_name)
                data[name]["yf_price"] = yf_price["price"]
            except:
                pass
        time.sleep(5)

def update_prices_dex():
    while True:
        assets.get_prices(tickers)
        time.sleep(1)

def update_redeem_dex():
    while True:
        redeem_assets.get_prices(redeemers)
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

def calc_redeem_volume(name: str):
    A,B=redeem_assets.get_liquidity(name)
    print(data_redeem[name]["premium"])
    amountin=0
    if data_redeem[name]["premium"] < 99.5:
        tokenin='USD'
        tokenout= name
        price = data_redeem[name]["dex_price"]
        target = 100 / data_redeem[name]["premium"] * data_redeem[name]["dex_price"]
        amountin= math.sqrt(target*A*B)-A
    if data_redeem[name]["premium"] > 100.5:
        tokenin=name
        tokenout='USD'
        price = data_redeem[name]["dex_price"]
        target = 100 / data_redeem[name]["premium"] * data_redeem[name]["dex_price"]
        amountin= math.sqrt(A*B/target)-B
    return amountin

def send_update():
    message = "Time: " + f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
    message += "Asset, Oracle/Dex, Premium\n"
    for name in data:
        message += f"{name}, {data[name]['dex_price']:.2f} jUSD / YF_Oracle: {data[name]['yf_price']:.2f} $, {data[name]['premium']:.2f} %\n"  #
    message += "jUSD Prices\n"
    for name in data_redeem:
        message += f"{name}, {1/data_redeem[name]['dex_price']:.2f} {name}/jUSD\n"  #
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

def update_jasset_oracle():
    for name in data:
        data_ = JAssets.get_price(name)
        data[name]["jasset_oracle"] = data_['price']
        data[name]["jasset_isPyth"] = data_['pyth']

def update_redeem_pools():
    for name in data_redeem:
        data_redeem[name]["dex_price"] = redeem_assets.get_price(name)
    for name in data_redeem:
        try:
            data_redeem[name]["premium"] = data_redeem[name]["dex_price"] / 1.0 * 100
        except:
            data_redeem[name]["premium"] = 100.0

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
        update_redeem_pools()
        send_update()
        while True:
            update_dex_premium()
            update_redeem_pools()
            if time.time()-t0 >=60*60:
                send_update()
                t0 = time.time()
            for name in data_redeem:
                premium_value = data_redeem[name]["premium"]
                if(premium_value>100.5) and time.time()-data_redeem[name]["time"]>60*30: # keep in mind that premium is defined in jUSD/USDT
                    amountin = calc_redeem_volume(name)
                    data_redeem[name]["time"] = time.time()
                    message = "Redeemen ist möglich!\n"
                    message += f"Swappe {amountin*1.003:.2f} {name} gegen jUSD um den Preis 1.00 zu erreichen\n"
                    bot.send_telegram_msg(message)

            for name in data:
                premium_value = data[name]["premium"]
                #print(premium_value)
                if abs(premium_value - 100) > 10.0 and premium_value != 0:
                    if time.time() - data[name]["time"] > 60*30:
                        amountin = calc_volume(name)
                        amountin = amountin * 1.003
                        data[name]["time"] = time.time()
                        message = "Asset, Oracle/Dex, Premium\n"
                        message += f"{name}, {data[name]['dex_price']:.2f} jUSD / YF_Oracle: {data[name]['yf_price']:.2f} $, {data[name]['premium']:.2f} %\n"
                        if premium_value - 100 < 0.0:
                            message += f"Swappe {amountin:.2f} jUSD gegen {name} damit Ratio bei 90 %\n"
                            bot.send_telegram_msg(message)
                        if premium_value - 100 > 0.0:
                            message += f"Swappe {amountin:.2f} {name} gegen jUSD damit Ratio bei 110 %\n"
                            bot.send_telegram_msg(message)
            for name in data:
                if abs(data[name]["premium"] - 100) < 9.5 and abs(data[name]["last_premium"] - 100) > 10 or abs(
                        data[name]["premium"] - 100) > 10.0 and abs(data[name]["last_premium"] - 100) < 9.5:
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

    thread = threading.Thread(target=update_redeem_dex)
    thread.start()

    thread = threading.Thread(target=run_bot)
    thread.start()

    bot.data = data
    bot.run()

