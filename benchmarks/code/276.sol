// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j) {
        i = 0;
        j = 0;

        while (i < 100) {
            j += 2;
            i++;
        }

        assert(j == 200);
    }

    function unknown() internal view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}