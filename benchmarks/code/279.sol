// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j) {
        require(i >= 1, "failed pre-condition");
        require(j >= 1, "failed pre-condition");
        require(i * i < j * j, "failed pre-condition");

        while (i < j) {
            j = j - i;
            if (j < i) {
                j = j + i;
                i = j - i;
                j = j - i;
            }
        }

        assert(j == i);
    }
}