// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int sn) {
        sn = 0;
        i = 1;
        while (i <= 8) {
            i = i + 1;
            sn = sn + 1;
        }
        if (sn != 0) {
            assert(sn == 8);
        }
    }
}