// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i) {
        require(i >= 0, "failed pre-condition");
        require(i <= 200, "failed pre-condition");
        while (i > 0) {
            i = i - 1;
        }
        assert(i >= 0);
    }
}