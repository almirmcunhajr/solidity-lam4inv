// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(x < y, "failed pre-condition");
        require(y <= 20000001, "failed pre-condition");

        while (x < y) {
            if (x < 0) {
                x = x + 7;
            } else {
                x = x + 10;
            }
            if (y < 0) {
                y = y - 10;
            } else {
                y = y + 3;
            }
        }

        assert(x >= y);
    }
}