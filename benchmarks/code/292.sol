// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int k) {
        require(i < j, "failed pre-condition");
        require(k > 0, "failed pre-condition");

        while (i < j) {
            k = k + 1;
            i = i + 1;
        }

        assert(k > j - i);
    }
}