// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int z) {
        require(x == y, "failed pre-condition");
        require(x >= 0, "failed pre-condition");
        require(x + y + z == 0, "failed pre-condition");

        while (x > 0) {
            x--;
            y--;
            z += 2;
        }

        assert(z <= 0);
    }
}