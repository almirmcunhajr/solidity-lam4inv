// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 0;
        y = 50;

        while (x < 100) {
            if (x < 50) {
                x = x + 1;
            } else {
                x = x + 1;
                y = y + 1;
            }
        }

        assert(y == 100);
    }
}