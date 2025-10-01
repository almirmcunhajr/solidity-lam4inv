// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int k, int n) {
        i = 0;
        k = 0;

        while (i < n) {
            i = i + 1;
            k = k + 1;
        }

        assert(k >= n);
    }
}