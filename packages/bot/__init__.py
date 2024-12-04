import sys
import os
import logging

from web3 import Web3
from dotenv import load_dotenv

from packages.bot.tokens import Tokens

load_dotenv()

# Import global variables
tokens = Tokens()

# Init logger
logger = logging.getLogger("ApollonArbitrageBot")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

# Load config
PRIVATE_KEY: str = os.getenv("PRIVATE_KEY")
ADDRESS = Web3().eth.account.from_key(PRIVATE_KEY).address
print(ADDRESS)
