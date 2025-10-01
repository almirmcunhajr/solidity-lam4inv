// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int z) {
        x = 0;
        z = 5000000;

        while (x < 10000000) {
            if (x >= 5000000) {
                z--;
            }
            x++;
        }

        assert(z == 0);
    }
}