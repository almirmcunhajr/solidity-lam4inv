// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int a, int c, int m, int j, int k) {
        j = 0;
        k = 0;

        while (k < c) {
            if (m < a) {
                m = a;
            }
            k = k + 1;
        }

        if (c > 0) {
            assert(a <= m);
        }
    }
}