// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int x, int y) {
        j = 0;
        i = 0;
        y = 1;
        while (i <= x) {
            i = i + 1;
            j = j + y;
        }
        if (i != j) {
            assert(y != 1);
        }
    }
}