// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int z, int w) {
        x = 0;
        y = 0;
        z = 0;
        w = 0;

        while (unknown()) {
            if (x >= 4) {
                x = x + 1;
                y = y + 2;
            } else if (y > 10 * w && z >= 100 * x) {
                y = 0 - y;
            } else {
                x = x + 1;
                y = y + 100;
            }
            w = w + 1;
            z = z + 10;
        }

        if (x >= 4) {
            assert(y > 2);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}