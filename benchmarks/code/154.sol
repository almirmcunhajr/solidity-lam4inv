// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int i, int j) {
        j = 0;
        require(x > 0, "failed pre-condition");
        i = 0;
        while (i < x) {
            j = j + 2;
            i = i + 1;
        }
        if (i >= x) {
            assert(j == 2 * x);
        }
    }
}