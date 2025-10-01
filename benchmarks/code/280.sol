// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(x < y, "failed pre-condition");
        while (x < y) {
            x = x + 100;
        }
        assert(x >= y);
    }
}