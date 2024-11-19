// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";

import {TroveFactory} from "../src/TroveFactory.sol";

contract DeployTroveFactory is Script {
    TroveFactory troveFactory;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        troveFactory = new TroveFactory();

        console.log("TroveFactory: ", address(troveFactory));

        vm.stopBroadcast();
    }
}
