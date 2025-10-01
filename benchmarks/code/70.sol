// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int x, int y) {
        x = 1;

        while (x <= n) {
            y = n - x;
            x = x + 1;
        }

        if (n > 0) {
            assert(y < n);
        }
    }
}