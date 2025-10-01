// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(x < y, "failed pre-condition");
        require(y <= 20000001, "failed pre-condition");
        while (x < y) {
            x = x + 100;
        }
        assert(x <= y + 99);
    }
}