from web3 import Web3
from eth_abi import decode
import json

def check_transaction_revert(tx_hash, rpc_url):
    """
    Debug a failed transaction to determine why it reverted.
    
    Args:
        tx_hash (str): Transaction hash to investigate
        rpc_url (str): Ethereum node RPC URL
    """
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    try:
        # Get transaction details
        tx = w3.eth.get_transaction(tx_hash)
        
        # Try to replay the transaction
        try:
            receipt = w3.eth.call({
                'to': tx['to'],
                'from': tx['from'],
                'data': tx['input'],
                'value': tx['value'],
                'gas': tx['gas'],
                'gasPrice': tx['gasPrice']
            }, tx['blockNumber'] - 1)
        except Exception as e:
            error = str(e)

            print(error)
            
            # Parse common revert reasons
            if "revert" in error.lower():
                # Try to decode custom error message
                if "0x08c379a0" in error:  # Error signature for Error(string)
                    error_data = error.split("0x08c379a0")[1]
                    decoded = decode(['string'], bytes.fromhex(error_data[8:]))[0]
                    print(f"Transaction reverted with message: {decoded}")
                    return
                    
                # Check for common errors
                if "insufficient funds" in error.lower():
                    print("Transaction reverted due to insufficient funds")
                elif "gas required exceeds allowance" in error.lower():
                    print("Transaction reverted due to out of gas")
                else:
                    print(f"Transaction reverted with error: {error}")
            else:
                print(f"Transaction failed with error: {error}")
            
            # Get contract ABI if available
            try:
                contract = w3.eth.contract(address=tx['to'])
                function_signature = tx['input'][:10]
                for abi_item in contract.abi:
                    if abi_item.get('type') == 'function':
                        if function_signature == w3.keccak(text=f"{abi_item['name']}({','.join([input['type'] for input in abi_item['inputs']])})").hex()[:10]:
                            print(f"\nFunction called: {abi_item['name']}")
                            break
            except:
                pass
                
    except Exception as e:
        print(f"Error retrieving transaction: {str(e)}")

# Example usage
if __name__ == "__main__":
    tx_hash = "0x4a0fb6982b5982c2109ff6e6088d6eabffae5d5dce0f8be7e5741b3fcf2e19f3"  # Replace with actual transaction hash
    rpc_url = "https://evm-rpc-testnet.sei-apis.com"  # Replace with your RPC URL
    check_transaction_revert(tx_hash, rpc_url)