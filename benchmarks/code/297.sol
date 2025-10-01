// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 0;
        y = 500000;

        while (x < 1000000) {
            if (x < 500000) {
                x = x + 1;
            } else {
                x = x + 1;
                y = y + 1;
            }
        }

        assert(y == x);
    }

    function unknown() internal view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}