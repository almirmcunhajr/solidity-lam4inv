// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint n, uint j, uint i, uint k, uint v4, uint v3, uint v2, uint v1, uint v5, uint v6, uint l) {
        i = 0;
        k = 0;
        j = 0;
        l = 0;
        v4 = 0;
        v3 = 0;
        v2 = 0;
        v1 = 0;
        v5 = 0;
        v6 = 0;
        require(n <= 20000001, "failed pre-condition");

        while (l < n) {
            if ((l % 9) == 0) {
                v6 = v6 + 1;
            } else if ((l % 8) == 0) {
                v5 = v5 + 1;
            } else if ((l % 7) == 0) {
                v1 = v1 + 1;
            } else if ((l % 6) == 0) {
                v2 = v2 + 1;
            } else if ((l % 5) == 0) {
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

        assert((i + j + k + v4 + v3 + v2 + v1 + v5 + v6) == l);
    }
}