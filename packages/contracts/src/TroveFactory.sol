// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import {IBase} from "./Interfaces/IBase.sol";
import {ISwapOperations} from "./Interfaces/ISwapOperations.sol";

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

    address public constant BORROWER_OPERATIONS =
        0xb56F7fd9c0B69380Af23efFE344CD2c4dc4315F5;
    address public constant SWAP_OPERATIONS =
        0xc847e2E9B01AA48c92a0252AF3887d095a4Ce31A;
    address public constant TROVE_MANAGER =
        0xB38bf2E7166f1d06D8C2253393d971a205BAd80E;
    address public constant PRICE_FEED =
        0xd703e3c76F33419f6dA166F980D1B6102d1B5836;
    address public constant jUSD = 0xA2efBedf2a9954aC0854933d148F9B5Df9C1FeE0;

    TroveHandler[] public troveHandlers;

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
        bytes[] memory priceUpdateData,
        IBase.MintMeta memory mintMeta
    ) external onlyOwner {
        IBase.TokenAmount[] memory tokenAmountArray;
        bool isLongPosition = deptToken.tokenAddress == jUSD ? true : false;

        // Create trove handler
        TroveHandler troveHandler = createTroveHandler();

        // Deposit collateral into trove handler
        troveHandler.deposit(
            collateralToken.tokenAddress,
            collateralToken.amount
        );

        // Open trove and add collateral
        tokenAmountArray = tokenInputToArray(collateralToken);
        troveHandler.openTrove(tokenAmountArray, priceUpdateData);

        // Open Position
        ISwapOperations.SwapAmount[] memory amounts;
        if (isLongPosition) {
            amounts = troveHandler.openLongPosition(
                deptToken.amount,
                0,
                newCollateralAddress,
                address(this),
                mintMeta,
                block.timestamp,
                priceUpdateData
            );
        } else {
            amounts = troveHandler.openShortPosition(
                deptToken.amount,
                0,
                deptToken.tokenAddress,
                address(this),
                mintMeta,
                block.timestamp,
                priceUpdateData
            );
        }

        // Add new collateral token to trove
        IERC20 newCollateralToken = IERC20(newCollateralAddress);
        tokenAmountArray = tokenInputToArray(
            TokenInput(
                address(newCollateralToken),
                newCollateralToken.balanceOf(address(this))
            )
        );
        troveHandler.addColl(
            tokenAmountArray,
            mintMeta.upperHint,
            mintMeta.lowerHint,
            priceUpdateData
        );

        // Withdraw init collateral token from trove
        troveHandler.withdrawColl(
            tokenAmountArray,
            mintMeta.upperHint,
            mintMeta.lowerHint,
            priceUpdateData
        );

        // Mint jUSD until trove is at 110%
        uint mintStableAmount = troveHandler.calculateMaxMintAmount(
            110e16,
            1e18
        );

        troveHandler.increaseStableDebt(
            mintStableAmount,
            mintMeta,
            priceUpdateData
        );

        // Withdraw tokens from TroveHandler to TroveFactory
        troveHandler.withdraw(
            collateralToken.tokenAddress,
            collateralToken.amount
        );

        troveHandler.withdraw(jUSD, mintStableAmount);

        // Emit event
        emit ExecutedArbitrage(
            address(troveHandler),
            isLongPosition,
            mintStableAmount
        );
    }

    /* ========== Deposit & Withdraw ========== */

    function deposit(address tokenAddress, uint amount) external {
        IERC20 token = IERC20(tokenAddress);
        token.transferFrom(msg.sender, address(this), amount);
    }

    function withdraw(address tokenAddress, uint amount) external onlyOwner {
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
}
