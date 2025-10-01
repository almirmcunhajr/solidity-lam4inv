// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int k, int n, int i, int j) {
        j = 0;
        i = 0;
        require(n >= 0, "failed pre-condition");
        require(n <= 20000001, "failed pre-condition");
        require(k >= 0, "failed pre-condition");
        require(k <= 20000001, "failed pre-condition");
        while (i <= n) {
            i = i + 1;
            j = j + 1;
        }
        if (i > n) {
            assert((k + i + j) > (2 * n));
        }
    }
}