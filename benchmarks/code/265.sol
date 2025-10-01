// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int i, int l) {
        i = l;
        require(l > 0, "failed pre-condition");
        while (i < n) {
            i = i + 1;
        }
        assert(l >= 1);
    }
}