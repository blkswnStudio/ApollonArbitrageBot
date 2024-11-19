from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

from adapter import TroveFactory


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider("https://evm-rpc-testnet.sei-apis.com"))
    tf = TroveFactory(w3, "0xE5737e5085B8d65F0aFAbc61B72d764bd47e2D26")
    tf.approve_token("0x5abdaEF2aa41B075B074ABE0711fB1cC6FB09284", 100)
    tx_hash: str = tf.execute("0x5abdaEF2aa41B075B074ABE0711fB1cC6FB09284", 100, 
    "0x2E5AE8fbE2e5cd9dA8710E1DDebe64A1BA121Ae4", 80, 
    "0xAE34739a521521DE17902999ff8FBb12394192a1")

    print(tx_hash)