// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 1;
        y = 0;
        while (y < 100000) {
            x = x + y;
            y = y + 1;
        }
        assert(x >= y);
    }
}