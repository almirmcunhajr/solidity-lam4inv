// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 1;
        while (x < y) {
            {
                x = x + x;
            }
        }
        assert(x >= 1);
    }
}