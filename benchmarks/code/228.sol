// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 0;
        while (x < 99) {
            if (y % 2 == 0) {
                x = x + 2;
            } else {
                x = x + 1;
            }
        }
        assert((x % 2) == (y % 2));
    }
}