// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x) {
        x = 268435441;
        while (x > 1) {
            x -= 2;
        }
        assert(x % 2 == 1);
    }
}