// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j) {
        i = 1;
        j = 20;
        while (j >= i) {
            i = i + 2;
            j = j - 1;
        }
        assert(j == 13);
    }
}