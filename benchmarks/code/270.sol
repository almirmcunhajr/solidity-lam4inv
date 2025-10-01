// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(y >= 0, "failed pre-condition");
        x = y;
        while (x != 0) {
            x = x - 1;
            y = y - 1;
        }
        assert(y == 0);
    }
}