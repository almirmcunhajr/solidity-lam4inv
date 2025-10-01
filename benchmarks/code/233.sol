// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x) {
        x = 0;
        while (x < 268435455) {
            x += 2;
        }
        assert(x % 2 == 0);
    }
}