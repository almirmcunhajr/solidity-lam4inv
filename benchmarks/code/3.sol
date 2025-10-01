// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int z) {
        x = 0;

        while (x < 5) {
            x += 1;
            if (z <= y) {
                y = z;
            }
        }

        assert(z >= y);
    }
}