// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int x, int y) {
        i = x;
        j = y;
        while (x != 0) {
            x = x - 1;
            y = y - 1;
        }
        if (y != 0) {
            assert(i != j);
        }
    }
}