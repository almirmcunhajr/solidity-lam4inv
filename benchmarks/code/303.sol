// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x) {
        x = 0;
        while (x < 100000000) {
            if (x < 10000000) {
                x++;
            } else {
                x += 2;
            }
        }
        assert((x % 2) == 0);
    }
}