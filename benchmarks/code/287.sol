// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(x < 100, "failed pre-condition");
        require(y < 100, "failed pre-condition");

        while (x < 100 && y < 100) {
            x = x + 1;
            y = y + 1;
        }

        assert(x == 100 || y == 100);
    }
}