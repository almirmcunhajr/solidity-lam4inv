// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = -5000;
        while (x < 0) {
            x = x + y;
            y = y + 1;
        }
        assert(y > 0);
    }
}