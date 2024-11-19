#!/bin/bash
source .env

forge script script/DeployTroveFactory.s.sol --broadcast --optimize --optimizer-runs 200 --private-key=$PRIVATE_KEY --rpc-url=$RPC_URL --legacy