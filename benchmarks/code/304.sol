// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(uint x, uint z) {
        x = 0;
        z = 0;

        while (x < 10000000) {
            if (x >= 5000000) {
                z = z + 2;
            }
            x++;
        }

        assert((z % 2) == 0);
    }
}