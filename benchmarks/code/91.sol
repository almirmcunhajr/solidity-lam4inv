// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 0;
        y = 0;

        while (y >= 0) {
            y = y + x;
        }

        assert(y >= 0);
    }
}