// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int i, int k, int j) {
        i = 0;
        j = 0;
        k = 0;
        require(n <= 20000001, "failed pre-condition");
        while (i < n) {
            i = i + 3;
            if ((i % 2) != 0) {
                j = j + 3;
            } else {
                k = k + 3;
            }
        }
        if (n > 0) {
            assert(i / 2 <= j);
        }
    }
}