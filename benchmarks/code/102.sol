// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int x) {
        x = 0;
        while (x < n) {
            x = x + 1;
        }
        if (n >= 0) {
            assert(x == n);
        }
    }
}