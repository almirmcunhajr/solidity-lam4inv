// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int k, int n) {
        i = 0;
        require(n >= 0, "failed pre-condition");
        require(n <= 20000001, "failed pre-condition");
        k = n;

        while (i < n) {
            k--;
            i += 2;
        }

        assert(2 * k >= n - 1);
    }
}