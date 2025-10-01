// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int k, int i, int j, int n, int turn) {
        k = 1;
        i = 1;
        j = 0;
        turn = 0;

        while ((turn >= 0) && (turn < 3)) {
            if ((turn == 0) && (i >= n)) {
                turn = 3;
            } else if ((turn == 1) && (j < i)) {
                k = k + i - j;
                j = j + 1;
            } else if ((turn == 1) && (j >= i)) {
                turn = 2;
            } else if (turn == 2) {
                i = i + 1;
                turn = 0;
            }
        }

        if (turn == 3) {
            assert(k >= n);
        }
    }
}