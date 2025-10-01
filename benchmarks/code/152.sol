// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int pvlen, int t, int k, int n, int j, int turn) {
        k = 0;
        i = 0;
        turn = 0;

        while (turn < 5) {
            if (turn == 0) {
                i = i + 1;
                if (unknown()) {
                    turn = 1;
                }
            } else if (turn == 1) {
                if (i > pvlen) {
                    pvlen = i;
                }
                i = 0;
                turn = 2;
            } else if (turn == 2) {
                t = i;
                i = i + 1;
                k = k + 1;
                if (unknown()) {
                    turn = 3;
                }
            } else if (turn == 3) {
                if (unknown()) {
                    turn = 4;
                }
            } else if (turn == 4) {
                n = i;
                j = 0;
                turn = 5;
            }
        }

        assert(k >= 0);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}