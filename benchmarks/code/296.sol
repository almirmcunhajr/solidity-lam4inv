// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x, uint y) {
        x = 0;
        y = 0;

        while (x < 1000000) {
            if (x < 500000) {
                y++;
            } else {
                y--;
            }
            x++;
        }

        assert(y == 0);
    }
}