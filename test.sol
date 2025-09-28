// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    int d1;
    int d2;
    int d3;
    int x1;
    int x2;
    int x3;

    constructor(int x2, int x3) {
        d1 = 1;
        d2 = 1;
        d3 = 1;
        x1 = 1;

        while (x1 > 0) {
            if (x2 > 0) {
                if (x3 > 0) {
                    x1 = x1 - d1;
                    x2 = x2 - d2;
                    x3 = x3 - d3;
                }
            }
        }

        assert(x2 >= 0);
    }
}
