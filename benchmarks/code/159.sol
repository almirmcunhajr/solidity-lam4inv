// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int j, int k) {
        j = 0;
        require(n > 0, "failed pre-condition");
        require(k > n, "failed pre-condition");
        while (j < n) {
            j = j + 1;
            k = k - 1;
        }
        if (j >= n) {
            assert(k >= 0);
        }
    }
}