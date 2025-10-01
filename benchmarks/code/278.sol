// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int k, int j) {
        require(k > i - j, "failed pre-condition");
        require(i < j, "failed pre-condition");

        while (i < j) {
            k = k + 1;
            i = i + 1;
        }

        assert(k > 0);
    }
}