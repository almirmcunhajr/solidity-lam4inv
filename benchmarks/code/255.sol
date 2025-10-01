// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int v) {
        v = 1;
        while (v <= 50) {
            v = v + 2;
        }
        assert(v <= 52);
    }
}