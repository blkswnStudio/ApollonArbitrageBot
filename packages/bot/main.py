from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

from adapter import TroveFactory


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider("https://evm-rpc-testnet.sei-apis.com"))
    tf = TroveFactory(w3, "0x181E9081c569cb1Bd29E6995DF0E32Fe824f23Da")
    tf.approve_token("0x5abdaEF2aa41B075B074ABE0711fB1cC6FB09284", 1000)
    tx_hash: str = tf.execute("0x5abdaEF2aa41B075B074ABE0711fB1cC6FB09284", 1000,
    "0x7938486225755BeC1fc202CA80799d27f108B33f", 4, 
    "0xAE34739a521521DE17902999ff8FBb12394192a1")

    print(tx_hash)
