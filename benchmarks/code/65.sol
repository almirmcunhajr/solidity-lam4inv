// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 1;
        while (x <= 100) {
            y = 100 - x;
            x = x + 1;
        }
        assert(y >= 0);
    }
}