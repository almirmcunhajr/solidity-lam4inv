// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x, uint y) {
        y = 1;

        while (unknown()) {
            if (x % 3 == 1) {
                x = x + 2;
                y = 0;
            } else {
                if (x % 3 == 2) {
                    x = x + 1;
                    y = 0;
                } else {
                    if (unknown()) {
                        x = x + 4;
                        y = 1;
                    } else {
                        x = x + 5;
                        y = 1;
                    }
                }
            }
        }

        if (y == 0) {
            assert(x % 3 == 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}