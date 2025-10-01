// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int x) {
        x = n;
        while (x > 0) {
            x = x - 1;
        }
        if (n >= 0) {
            assert(x == 0);
        }
    }
}