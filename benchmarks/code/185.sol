// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int n, int k) {
        i = 0;
        j = 0;
        require(n == 1 || n == 2, "failed pre-condition");
        while (i <= k) {
            i = i + 1;
            j = j + n;
        }
        if (i > k && i != j) {
            assert(n != 1);
        }
    }
}