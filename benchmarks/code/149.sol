// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int i, int j) {
        x = 0;
        y = 0;
        j = 0;
        i = 0;

        while (unknown()) {
            x = x + 1;
            y = y + 1;
            i = x + i;
            if (unknown()) {
                j = y + j;
            } else {
                j = y + j + 1;
            }
        }

        assert(j >= i);
    }

    function unknown() internal view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}