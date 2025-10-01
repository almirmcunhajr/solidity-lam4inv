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
                y = y + 3;
                z = z + 10;
                w = w + 10;
            } else if (x >= z && w > y) {
                x = 0 - x;
                y = 0 - y;
            } else {
                x = x + 1;
                y = y + 2;
            }
        }

        assert(3 * x >= y);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}