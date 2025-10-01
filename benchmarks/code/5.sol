// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int size, int y, int z) {
        x = 0;
        while (x < size) {
            x += 1;
            if (z <= y) {
                y = z;
            }
        }
        if (size > 0) {
            assert(z >= y);
        }
    }
}