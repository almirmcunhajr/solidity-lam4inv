// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int p, int c, int cl) {
        p = 0;
        c = cl;

        while ((p < 4) && (cl > 0)) {
            cl = cl - 1;
            p = p + 1;
        }

        if (p != 4) {
            assert(c < 4);
        }
    }
}