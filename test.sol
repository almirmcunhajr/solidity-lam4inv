// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    int x;
    int y;

    constructor() {
        // pre-conditions
        x = 1;
        y = 0;

        // loop body
        while (y < 100000) {
            x = x + y;
            y = y + 1;
        }

        // post-condition
        assert(x >= y);
    }
}
