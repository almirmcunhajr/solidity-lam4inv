// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int k, int i) {
        n = 0;
        i = 0;
        require(k >= 0, "failed pre-condition");
        require(k <= 20000001, "failed pre-condition");
        while (i < 2 * k) {
            if (i % 2 == 0) {
                n = n + 1;
            }
            i = i + 1;
        }
        assert(n == k);
    }
}