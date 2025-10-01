// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int size, int sn) {
        sn = 0;
        i = 1;
        require(size >= 1, "failed pre-condition");
        while (i <= size) {
            i = i + 1;
            sn = sn + 1;
        }
        if (sn != 0) {
            assert(sn == size);
        }
    }
}