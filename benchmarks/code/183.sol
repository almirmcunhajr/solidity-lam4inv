// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int i, int t) {
        i = 0;
        require(x != y, "failed pre-condition");
        require(t == y, "failed pre-condition");
        while (x > 0) {
            y = x + y;
        }
        assert(y >= t);
    }
}