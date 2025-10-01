// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(y <= 1000000, "failed pre-condition");
        while (x < 100 && y > 0) {
            x = x + y;
        }
        if (y <= 0 || (y > 0 && x >= 100)) {
            assert(y <= 0 || (x >= 100 && y > 0));
        }
    }
}