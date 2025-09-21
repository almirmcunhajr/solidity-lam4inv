// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    int i;
    int j;
    int x;
    int y;

    constructor(int _x, int _y) {
        // pre-conditions
        x = 0;
        y = 0;
        i = x;
        j = y;

        // loop body
        while (x != 0) {
            x = x - 1;
            y = y - 1;
        }

        // post-condition
        if (y != 0) {
            assert(i != j);
        }
    }
}
