TROVE_FACTORY_ABI: dict = [{"type":"constructor","inputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"BORROWER_OPERATIONS","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"PRICE_FEED","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"SWAP_OPERATIONS","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"TROVE_MANAGER","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"createTroveHandler","inputs":[],"outputs":[{"name":"","type":"address","internalType":"contract TroveHandler"}],"stateMutability":"nonpayable"},{"type":"function","name":"deposit","inputs":[{"name":"tokenAddress","type":"address","internalType":"address"},{"name":"amount","type":"uint256","internalType":"uint256"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"execute","inputs":[{"name":"troveHandlerAddress","type":"address","internalType":"address"},{"name":"collateralToken","type":"tuple","internalType":"struct TroveFactory.TokenInput","components":[{"name":"tokenAddress","type":"address","internalType":"address"},{"name":"amount","type":"uint256","internalType":"uint256"}]},{"name":"deptToken","type":"tuple","internalType":"struct TroveFactory.TokenInput","components":[{"name":"tokenAddress","type":"address","internalType":"address"},{"name":"amount","type":"uint256","internalType":"uint256"}]},{"name":"newCollateralToken","type":"tuple","internalType":"struct TroveFactory.TokenInput","components":[{"name":"tokenAddress","type":"address","internalType":"address"},{"name":"amount","type":"uint256","internalType":"uint256"}]},{"name":"priceUpdateData","type":"bytes[]","internalType":"bytes[]"},{"name":"mintMeta","type":"tuple","internalType":"struct IBase.MintMeta","components":[{"name":"upperHint","type":"address","internalType":"address"},{"name":"lowerHint","type":"address","internalType":"address"},{"name":"maxFeePercentage","type":"uint256","internalType":"uint256"}]}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"jUSD","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"owner","inputs":[],"outputs":[{"name":"","type":"address","internalType":"address"}],"stateMutability":"view"},{"type":"function","name":"renounceOwnership","inputs":[],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"setOwnerForAllTroveHandlers","inputs":[{"name":"newOwner","type":"address","internalType":"address"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"setOwnerForTroveHandler","inputs":[{"name":"troveHandler","type":"address","internalType":"contract TroveHandler"},{"name":"newOwner","type":"address","internalType":"address"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"transferOwnership","inputs":[{"name":"newOwner","type":"address","internalType":"address"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"troveHandlers","inputs":[{"name":"","type":"uint256","internalType":"uint256"}],"outputs":[{"name":"","type":"address","internalType":"contract TroveHandler"}],"stateMutability":"view"},{"type":"function","name":"withdraw","inputs":[{"name":"tokenAddress","type":"address","internalType":"address"},{"name":"amount","type":"uint256","internalType":"uint256"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"event","name":"ExecutedArbitrage","inputs":[{"name":"troveHandler","type":"address","indexed":true,"internalType":"address"},{"name":"isLong","type":"bool","indexed":false,"internalType":"bool"},{"name":"mintedStableAmount","type":"uint256","indexed":false,"internalType":"uint256"}],"anonymous":false},{"type":"event","name":"OwnershipTransferred","inputs":[{"name":"previousOwner","type":"address","indexed":true,"internalType":"address"},{"name":"newOwner","type":"address","indexed":true,"internalType":"address"}],"anonymous":false},{"type":"error","name":"OwnableInvalidOwner","inputs":[{"name":"owner","type":"address","internalType":"address"}]},{"type":"error","name":"OwnableUnauthorizedAccount","inputs":[{"name":"account","type":"address","internalType":"address"}]}]