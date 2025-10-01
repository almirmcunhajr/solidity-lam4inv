// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x) {
        x = 100;
        while (x > 0) {
            x = x - 1;
        }
        assert(x == 0);
    }
}