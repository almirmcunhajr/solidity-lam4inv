// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(y >= 0, "failed pre-condition");
        require(y <= 20000001, "failed pre-condition");
        x = 4 * y;
        while (x > 0) {
            x -= 4;
            y--;
        }
        assert(y >= 0);
    }
}