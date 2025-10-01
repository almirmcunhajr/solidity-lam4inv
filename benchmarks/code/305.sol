// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x) {
        x = 0;

        while (x < 1000000) {
            if (x < 750000) {
                x++;
            } else {
                x = x + 2;
            }
        }

        assert(x == 1000000);
    }
}