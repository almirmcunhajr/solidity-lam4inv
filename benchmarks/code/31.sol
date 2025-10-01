// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int x) {
        x = n;
        while (x > 1) {
            x = x - 1;
        }
        if (x != 1) {
            assert(n <= 0);
        }
    }
}