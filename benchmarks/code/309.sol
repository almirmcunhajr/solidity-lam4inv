// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint n, uint j, uint i, uint k, uint v4, uint v3, uint l) {
        i = 0;
        k = 0;
        j = 0;
        l = 0;
        v4 = 0;
        v3 = 0;
        require(n <= 20000001, "failed pre-condition");

        while (l < n) {
            if ((l % 5) == 0) {
                v3 = v3 + 1;
            } else if ((l % 4) == 0) {
                v4 = v4 + 1;
            } else if ((l % 3) == 0) {
                i = i + 1;
            } else if ((l % 2) == 0) {
                j = j + 1;
            } else {
                k = k + 1;
            }
            l = l + 1;
        }

        assert((i + j + k + v4 + v3) == l);
    }
}