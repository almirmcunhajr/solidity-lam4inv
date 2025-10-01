// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint n, uint j, uint i, uint l) {
        i = 0;
        j = 0;
        l = 0;
        require(n <= 20000001, "failed pre-condition");

        while (l < n) {
            if ((l % 2) == 0) {
                i = i + 1;
            } else {
                j = j + 1;
            }
            l = l + 1;
        }

        assert((i + j) == l);
    }
}