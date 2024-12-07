// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

import {IBase} from "./Interfaces/IBase.sol";
import {ISwapOperations} from "./Interfaces/ISwapOperations.sol";
import {ITokenManager} from "./Interfaces/ITokenManager.sol";
import {IPriceFeed} from "./Interfaces/IPriceFeed.sol";

import {TroveHandler} from "./TroveHandler.sol";

contract TroveFactory is Ownable {
    constructor() Ownable(msg.sender) {}

    struct TokenInput {
        address tokenAddress;
        uint amount;
    }

    event ExecutedArbitrage(
        address indexed troveHandler,
        bool isLong,
        uint mintedStableAmount
    );

    /* ========== STATE VARIABLES ========== */

    uint constant DECIMALS = 1e18;

    address public constant BORROWER_OPERATIONS =
        0xb005fC27a8404d0AE7FB5081F57573d2c45CB7E0;
    address public constant SWAP_OPERATIONS =
        0xB89536EF8e99B3b6F3db2A6D369A95ad1338Fbfa;
    address public constant TROVE_MANAGER =
        0x70829AdD66Bf095fff0F04BF7E1D00123af28664;
    address public constant TOKEN_MANAGER =
        0x55cFe185028A55143376c271D4daAFDca57d7fA8;
    address public constant PRICE_FEED =
        0x2eA326623a323940BcA88bdA24dDc2e8D657749c;
    address public constant jUSD = 0xAE34739a521521DE17902999ff8FBb12394192a1;

    ITokenManager tokenManager = ITokenManager(TOKEN_MANAGER);
    IPriceFeed priceFeed = IPriceFeed(PRICE_FEED);

    IBase.MintMeta zeroMintMeta = IBase.MintMeta(address(0), address(0), 5e16);

    TroveHandler[] public troveHandlers;

    /* ========== Information ========== */

    function getDebtTokenAddresses() external view returns (address[] memory) {
        return tokenManager.getDebtTokenAddresses();
    }

    function getCollTokenAddresses() external view returns (address[] memory) {
        return tokenManager.getCollTokenAddresses();
    }

    /* ========== TroveHandler ========== */

    function createTroveHandler() public onlyOwner returns (TroveHandler) {
        TroveHandler troveHandler = new TroveHandler(
            BORROWER_OPERATIONS,
            SWAP_OPERATIONS,
            TROVE_MANAGER,
            PRICE_FEED
        );
        troveHandlers.push(troveHandler);
        return troveHandler;
    }

    function setOwnerForTroveHandler(
        TroveHandler troveHandler,
        address newOwner
    ) public onlyOwner {
        troveHandler.transferOwnership(newOwner);
    }

    function setOwnerForAllTroveHandlers(address newOwner) external onlyOwner {
        uint length = troveHandlers.length;
        for (uint i = 0; i < length; ) {
            setOwnerForTroveHandler(troveHandlers[i], newOwner);
        }
    }

    function execute(
        TokenInput memory collateralToken,
        TokenInput memory deptToken,
        address newCollateralAddress,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        IBase.TokenAmount[] memory tokenAmountArray;
        bool isLongPosition = deptToken.tokenAddress == jUSD ? true : false;
        uint updateFee = priceFeed.getPythUpdateFee(priceUpdateData);
        require(
            msg.value != updateFee * 4,
            "Not enough fee to update pyth prices"
        );

        // Deposit collateral into factory
        deposit(collateralToken.tokenAddress, collateralToken.amount);

        // Create trove handler
        TroveHandler troveHandler = createTroveHandler();

        // Deposit collateral into trove handler
        approve(
            collateralToken.tokenAddress,
            address(troveHandler),
            collateralToken.amount
        );
        troveHandler.deposit(
            collateralToken.tokenAddress,
            collateralToken.amount
        );

        // Open trove and add collateral
        tokenAmountArray = tokenInputToArray(collateralToken);
        troveHandler.openTrove{value: updateFee}(
            tokenAmountArray,
            priceUpdateData
        );

        // Open Long or Short Position
        ISwapOperations.SwapAmount[] memory amounts;
        if (isLongPosition) {
            amounts = troveHandler.openLongPosition{value: updateFee}(
                deptToken.amount,
                0,
                newCollateralAddress,
                address(troveHandler),
                zeroMintMeta,
                block.timestamp,
                priceUpdateData
            );
        } else {
            amounts = troveHandler.openShortPosition{value: updateFee}(
                deptToken.amount,
                0,
                deptToken.tokenAddress,
                address(troveHandler),
                zeroMintMeta,
                block.timestamp,
                priceUpdateData
            );
        }

        // Mint maximum amount of jUSD as profit
        uint amountOut = amounts[amounts.length - 1].amount;
        (uint newCollateralTokenPrice, , ) = priceFeed.getPrice(
            newCollateralAddress
        );
        uint amountOutUSD = (amountOut * newCollateralTokenPrice) / DECIMALS;

        (, uint currentDept) = troveHandler.getUSDValues();
        uint maximumDept = (amountOutUSD * DECIMALS) / 1105e15;
        require(
            maximumDept > currentDept,
            string(
                abi.encodePacked(
                    "Maximum dept is smaller than current dept: Maximum Dept: ",
                    toString(maximumDept),
                    " Current Dept: ",
                    toString(currentDept)
                )
            )
        );

        uint mintAmount = maximumDept - currentDept;
        troveHandler.increaseStableDebt{value: updateFee}(
            mintAmount,
            zeroMintMeta,
            priceUpdateData
        );

        // Add new collateral token to trove
        tokenAmountArray = tokenInputToArray(
            TokenInput(newCollateralAddress, amountOut)
        );
        troveHandler.addColl{value: updateFee}(
            tokenAmountArray,
            zeroMintMeta.upperHint,
            zeroMintMeta.lowerHint,
            priceUpdateData
        );

        // Withdraw init collateral token from trove
        tokenAmountArray = tokenInputToArray(
            TokenInput(
                address(collateralToken.tokenAddress),
                collateralToken.amount
            )
        );
        troveHandler.withdrawColl{value: updateFee}(
            tokenAmountArray,
            zeroMintMeta.upperHint,
            zeroMintMeta.lowerHint,
            priceUpdateData
        );

        // Withdraw tokens from TroveHandler to TroveFactory
        troveHandler.withdraw(
            collateralToken.tokenAddress,
            collateralToken.amount
        );

        troveHandler.withdraw(jUSD, mintAmount);

        // Withdraw from factory to address
        withdraw(collateralToken.tokenAddress, collateralToken.amount);
        withdraw(jUSD, mintAmount);

        // Emit event
        emit ExecutedArbitrage(
            address(troveHandler),
            isLongPosition,
            mintAmount
        );
    }

    /* ========== Deposit & Withdraw ========== */

    function deposit(address tokenAddress, uint amount) public {
        IERC20 token = IERC20(tokenAddress);
        token.transferFrom(msg.sender, address(this), amount);
    }

    function withdraw(address tokenAddress, uint amount) public onlyOwner {
        IERC20 token = IERC20(tokenAddress);
        token.transfer(msg.sender, amount);
    }

    /* ========== Helper ========== */

    function tokenInputToArray(
        TokenInput memory tokenInput
    ) internal pure returns (IBase.TokenAmount[] memory tokenAmountArray) {
        tokenAmountArray = new IBase.TokenAmount[](1);
        tokenAmountArray[0] = IBase.TokenAmount(
            tokenInput.tokenAddress,
            tokenInput.amount
        );
        return tokenAmountArray;
    }

    function approve(
        address tokenAddress,
        address spender,
        uint value
    ) internal {
        IERC20 token = IERC20(tokenAddress);
        token.approve(spender, value);
    }

    function toString(uint256 value) internal pure returns (string memory) {
        return Strings.toString(value);
    }
}
