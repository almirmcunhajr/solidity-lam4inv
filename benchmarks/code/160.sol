// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int i, int j) {
        x = i;
        y = j;
        while (x != 0) {
            x = x - 1;
            y = y - 1;
        }
        if (i == j) {
            assert(y == 0);
        }
    }
}