// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int k, int n) {
        require(k >= 0, "failed pre-condition");
        require(n >= 0, "failed pre-condition");
        i = 0;
        j = 0;
        while (i <= n) {
            i = i + 1;
            j = j + i;
        }
        assert((i + (j + k)) > (2 * n));
    }
}