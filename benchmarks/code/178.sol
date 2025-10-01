// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int n) {
        x = 0;
        require(n > 0, "failed pre-condition");
        while (x < n) {
            x = x + 1;
        }
        if (x >= n) {
            assert(x == n);
        }
    }
}