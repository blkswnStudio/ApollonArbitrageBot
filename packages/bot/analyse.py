from web3 import Web3
from eth_abi import decode
import json

class TransactionAnalyzer:
    def __init__(self, node_url):
        self.w3 = Web3(Web3.HTTPProvider(node_url))
        
    def get_transaction_error(self, tx_hash):
        """
        Analyzes a failed transaction and returns detailed error information
        
        Args:
            tx_hash (str): Transaction hash to analyze
        
        Returns:
            dict: Detailed error analysis
        """
        # Get transaction details
        tx = self.w3.eth.get_transaction(tx_hash)
        tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        
        # If transaction was successful, return early
        if tx_receipt['status'] == 1:
            return {"status": "success", "message": "Transaction was successful"}
        
        # Get debug trace
        trace = self.w3.provider.make_request(
            "debug_traceTransaction", 
            [tx_hash, {"tracer": "callTracer"}]
        )
        
        # Initialize error analysis
        error_analysis = {
            "status": "failed",
            "gas_used": tx_receipt['gasUsed'],
            "gas_limit": tx['gas'],
            "errors": []
        }
        
        # Check common failure reasons
        self._check_gas_issues(tx, tx_receipt, error_analysis)
        self._check_revert_reason(tx, tx_receipt, error_analysis)
        self._analyze_internal_calls(trace, error_analysis)
        
        return error_analysis
            
    def _check_gas_issues(self, tx, receipt, analysis):
        """Check for gas-related issues"""
        if receipt['gasUsed'] >= tx['gas']:
            analysis['errors'].append({
                "type": "gas_out",
                "message": "Transaction ran out of gas",
                "details": f"Gas used: {receipt['gasUsed']}, Gas limit: {tx['gas']}"
            })
            
    def _check_revert_reason(self, tx, receipt, analysis):
        """Extract revert reason if available"""
        try:
            # Try to get revert reason from receipt status
            result = self.w3.eth.call({
                'to': receipt['to'],
                'from': receipt['from'],
                'data': tx['input'],
                'gas': tx['gas'],
                'value': tx['value'],
            }, receipt['blockNumber'] - 1)
        except Exception as e:
            error_msg = str(e)
            if "revert" in error_msg.lower():
                # Parse custom error data if available
                print(error_msg)
                if "0x08c379a0" in error_msg:  # Error(string) signature
                    error_data = error_msg.split("0x08c379a0")[1]
                    decoded = decode(['string'], bytes.fromhex(error_data[8:]))[0]
                    analysis['errors'].append({
                        "type": "revert",
                        "message": decoded,
                        "details": "Custom revert message from contract"
                    })
                else:
                    analysis['errors'].append({
                        "type": "revert",
                        "message": error_msg,
                        "details": "Generic revert"
                    })
                    
    def _analyze_internal_calls(self, trace, analysis):
        """Analyze internal contract calls from debug trace"""
        if 'result' in trace and 'calls' in trace['result']:
            for call in trace['result']['calls']:
                if call.get('error'):
                    analysis['errors'].append({
                        "type": "internal_call",
                        "message": f"Failed call to {call['to']}",
                        "details": call['error']
                    })

def main():
    # Example usage
    node_url = "https://evm-rpc-testnet.sei-apis.com"
    analyzer = TransactionAnalyzer(node_url)
    
    tx_hash = "0xf27690ac80ba4e92c0f9f22a397163ef52fafed6c0c54e9b631b2e2f6faeb10b"  # Replace with actual transaction hash
    result = analyzer.get_transaction_error(tx_hash)
    
    print("\nTransaction Analysis:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()