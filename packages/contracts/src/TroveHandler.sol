// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import {IBorrowerOperations} from "./Interfaces/IBorrowerOperations.sol";
import {ISwapOperations} from "./Interfaces/ISwapOperations.sol";
import {ITroveManager} from "./Interfaces/ITroveManager.sol";
import {IPriceFeed} from "./Interfaces/IPriceFeed.sol";

contract TroveHandler is Ownable {
    constructor(
        address borrowOperationsAddress,
        address swapOperationsAddress,
        address troveManagerAddress,
        address priceFeedAddress
    ) Ownable(msg.sender) {
        borrowOperations = IBorrowerOperations(borrowOperationsAddress);
        swapOperations = ISwapOperations(swapOperationsAddress);
        troveManager = ITroveManager(troveManagerAddress);
        priceFeed = IPriceFeed(priceFeedAddress);
    }

    /* ========== STATE VARIABLES ========== */

    uint constant DECIMALS = 1e18;

    IBorrowerOperations borrowOperations;
    ISwapOperations swapOperations;
    ITroveManager troveManager;
    IPriceFeed priceFeed;

    bool public isTroveOpen = false;

    /* ========== Trove Info========== */

    function getUSDValues() public view returns (uint, uint) {
        IPriceFeed.PriceCache memory priceCache = priceFeed.buildPriceCache();
        (, uint collInUSD, uint debtInUSD) = troveManager
            .getCurrentTrovesUSDValues(priceCache, address(this));
        return (collInUSD, debtInUSD);
    }

    function getHeath() public view returns (uint) {
        (uint collInUSD, uint debtInUSD) = getUSDValues();
        return (collInUSD / debtInUSD) * DECIMALS;
    }

    function calculateMaxMintAmount(
        uint targetHealth,
        uint assetPrice
    ) public view returns (uint) {
        (uint collInUSD, uint debtInUSD) = getUSDValues();
        uint currentHealth = getHeath();
        if (currentHealth <= targetHealth) {
            return 0;
        }

        uint maxDebtUSD = (collInUSD * DECIMALS) / targetHealth;
        if (maxDebtUSD <= debtInUSD) {
            return 0;
        }

        uint maxMintUSD = maxDebtUSD - debtInUSD;
        return maxMintUSD / assetPrice;
    }

    /* ========== TroveBorrowOperations ========== */

    function openTrove(
        IBorrowerOperations.TokenAmount[] memory collateral,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        approveTokenAmount(collateral, address(borrowOperations));
        borrowOperations.openTrove{value: msg.value}(
            collateral,
            priceUpdateData
        );
        isTroveOpen = true;
    }

    function addColl(
        IBorrowerOperations.TokenAmount[] memory collateral,
        address upperHint,
        address lowerHint,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        approveTokenAmount(collateral, address(borrowOperations));
        borrowOperations.addColl{value: msg.value}(
            collateral,
            upperHint,
            lowerHint,
            priceUpdateData
        );
    }

    function withdrawColl(
        IBorrowerOperations.TokenAmount[] memory collateral,
        address upperHint,
        address lowerHint,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        borrowOperations.withdrawColl{value: msg.value}(
            collateral,
            upperHint,
            lowerHint,
            priceUpdateData
        );
    }

    function increaseDebt(
        address borrower,
        address to,
        IBorrowerOperations.TokenAmount[] memory debts,
        IBorrowerOperations.MintMeta memory meta
    ) external payable onlyOwner {
        borrowOperations.increaseDebt(borrower, to, debts, meta);
    }

    function increaseStableDebt(
        uint stableAmount,
        IBorrowerOperations.MintMeta memory meta,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        borrowOperations.increaseStableDebt{value: msg.value}(
            stableAmount,
            meta,
            priceUpdateData
        );
    }

    function repayDebt(
        IBorrowerOperations.TokenAmount[] memory debts,
        address upperHint,
        address lowerHint,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        approveTokenAmount(debts, address(borrowOperations));
        borrowOperations.repayDebt{value: msg.value}(
            debts,
            upperHint,
            lowerHint,
            priceUpdateData
        );
    }

    function repayDebtFromPoolBurn(
        address borrower,
        IBorrowerOperations.TokenAmount[] memory debts,
        address upperHint,
        address lowerHint
    ) external onlyOwner {
        borrowOperations.repayDebtFromPoolBurn(
            borrower,
            debts,
            upperHint,
            lowerHint
        );
    }

    function closeTrove(
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        borrowOperations.closeTrove{value: msg.value}(priceUpdateData);
        isTroveOpen = false;
    }

    function claimCollateral() external onlyOwner {
        borrowOperations.claimCollateral();
    }

    function claimUnassignedAssets(
        uint percentage,
        address upperHint,
        address lowerHint,
        bytes[] memory priceUpdateData
    ) external payable onlyOwner {
        borrowOperations.claimUnassignedAssets{value: msg.value}(
            percentage,
            upperHint,
            lowerHint,
            priceUpdateData
        );
    }

    /* ========== TroveSwapFunctions ========== */

    function openLongPosition(
        uint stableToMintIn,
        uint debtOutMin,
        address debtTokenAddress,
        address to,
        ISwapOperations.MintMeta memory mintMeta,
        uint deadline,
        bytes[] memory priceUpdateData
    )
        external
        payable
        onlyOwner
        returns (ISwapOperations.SwapAmount[] memory amounts)
    {
        return
            swapOperations.openLongPosition{value: msg.value}(
                stableToMintIn,
                debtOutMin,
                debtTokenAddress,
                to,
                mintMeta,
                deadline,
                priceUpdateData
            );
    }

    function openShortPosition(
        uint debtToMintIn,
        uint stableOutMin,
        address debtTokenAddress,
        address to,
        ISwapOperations.MintMeta memory mintMeta,
        uint deadline,
        bytes[] memory priceUpdateData
    )
        external
        payable
        onlyOwner
        returns (ISwapOperations.SwapAmount[] memory amounts)
    {
        return
            swapOperations.openShortPosition{value: msg.value}(
                debtToMintIn,
                stableOutMin,
                debtTokenAddress,
                to,
                mintMeta,
                deadline,
                priceUpdateData
            );
    }

    /* ========== Helper ========== */

    function approve(
        address tokenAddress,
        address spender,
        uint value
    ) internal {
        IERC20 token = IERC20(tokenAddress);
        token.approve(spender, value);
    }

    function approveTokenAmount(
        IBorrowerOperations.TokenAmount[] memory tokenAmount,
        address spender
    ) internal {
        uint length = tokenAmount.length;
        for (uint i = 0; i < length; i++) {
            approve(
                tokenAmount[i].tokenAddress,
                spender,
                tokenAmount[i].amount
            );
        }
    }

    /* ========== Deposit & Withdraw ========== */

    function deposit(address tokenAddress, uint amount) public onlyOwner {
        IERC20 token = IERC20(tokenAddress);
        token.transferFrom(msg.sender, address(this), amount);
    }

    function withdraw(address tokenAddress, uint amount) external onlyOwner {
        IERC20 token = IERC20(tokenAddress);
        token.transfer(msg.sender, amount);
    }
}
