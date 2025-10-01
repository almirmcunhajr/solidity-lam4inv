// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int r) {
        require(r > i + j, "failed pre-condition");
        while (i > 0) {
            i = i - 1;
            j = j + 1;
        }
        assert(r > i + j);
    }
}