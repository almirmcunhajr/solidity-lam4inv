// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int c, int n) {
        i = 0;
        c = 0;
        require(n > 0, "failed pre-condition");
        while (i < n) {
            c = c + i;
            i = i + 1;
        }
        if (i >= n) {
            assert(c >= 0);
        }
    }
}