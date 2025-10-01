// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int w, int z) {
        w = 1;
        z = 0;
        x = 0;
        y = 0;

        while (unknown()) {
            if (w == 1 && z == 0) {
                x = x + 1;
                w = 0;
                y = y + 1;
                z = 1;
            } else if (w != 1 && z == 0) {
                y = y + 1;
                z = 1;
            } else if (w == 1 && z != 0) {
                x = x + 1;
                w = 0;
            } else if (w != 1 && z != 0) {
                continue;
            }
        }

        assert(x == y);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}