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

        if (y <= 2) {
            assert(x < 4);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}