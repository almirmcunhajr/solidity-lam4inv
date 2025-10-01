// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint n, uint j, uint i, uint k) {
        i = 0;
        k = 0;
        j = 0;
        require(n <= 20000001, "failed pre-condition");
        while (i < n) {
            i = i + 3;
            j = j + 3;
            k = k + 3;
        }
        assert(k == j);
    }
}