// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 0;
        y = 0;

        while (unknown()) {
            if (x >= 4) {
                x = x + 1;
                y = y + 1;
            } else if (x < 0) {
                y = y - 1;
            } else {
                x = x + 1;
                y = y + 100;
            }
        }

        if (x >= 4) {
            assert(y > 2);
        }
    }

    function unknown() private view returns (bool) {
        return uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number))) % 2 == 0;
    }
}