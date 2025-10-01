// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int m, int x, int y) {
        x = 0;
        y = m;
        require(n >= 0, "failed pre-condition");
        require(m >= 0, "failed pre-condition");
        require(m < n, "failed pre-condition");
        while (x < n) {
            if (x + 1 <= m) {
                x = x + 1;
            } else if (x + 1 > m) {
                x = x + 1;
                y = y + 1;
            }
        }
        if (x >= n) {
            assert(y == n);
        }
    }
}