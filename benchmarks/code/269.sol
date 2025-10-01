// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int sum, int n) {
        require(n >= 0, "failed pre-condition");
        sum = 0;
        i = 0;
        while (i < n) {
            sum = sum + i;
            i = i + 1;
        }
        assert(sum >= 0);
    }
}