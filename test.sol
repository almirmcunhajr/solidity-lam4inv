// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    int x;
    int y;

    constructor() {
        x = 1;
        y = 0;

        while (y < 1024) {
            x = 0;
            y = y + 1;
        }

       assert(x == 0);
    }
}
