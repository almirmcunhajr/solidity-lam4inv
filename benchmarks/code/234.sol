// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x, uint N) {
        x = 0;
        while (x < N) {
            x += 2;
        }
        assert(x % 2 == 0);
    }
}