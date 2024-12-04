import os
import sys

from web3 import Web3
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")))

load_dotenv()

from packages.bot.bot import Bot


if __name__ == "__main__":
    bot = Bot()
    bot.start(1)
