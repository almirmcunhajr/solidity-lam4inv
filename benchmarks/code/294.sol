// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int xa, int ya) {
        require(xa + ya > 0, "failed pre-condition");
        while (xa > 0) {
            xa--;
            ya++;
        }
        assert(ya >= 0);
    }
}