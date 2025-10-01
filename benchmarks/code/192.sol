// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int b, int n) {
        i = 0;
        require(i < n, "failed pre-condition");
        while (i < n && b != 0) {
            i = i + 1;
        }
        if (i >= n) {
            assert(i == n && b != 0);
        }
    }
}