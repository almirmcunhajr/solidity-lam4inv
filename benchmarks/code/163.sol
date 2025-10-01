// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int b, int j, int n, int flag) {
        j = 0;
        b = 0;
        require(n > 0, "failed pre-condition");

        while (b < n) {
            if (flag == 1) {
                j = j + 1;
                b = b + 1;
            } else if (flag != 1) {
                b = b + 1;
            }
        }

        if (flag == 1) {
            assert(j == n);
        }
    }
}