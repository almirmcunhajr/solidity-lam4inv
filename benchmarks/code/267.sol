// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int k, int j, int n) {
        require(n >= 1, "failed pre-condition");
        require(k >= n, "failed pre-condition");
        j = 0;
        while (j <= n - 1) {
            j = j + 1;
            k = k - 1;
        }
        assert(k >= 0);
    }
}