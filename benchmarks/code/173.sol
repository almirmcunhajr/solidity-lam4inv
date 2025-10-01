// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int i, int j, int turn) {
        x = 0;
        y = 0;
        i = 0;
        j = 0;
        turn = 0;

        while ((turn >= 0) && (turn < 3)) {
            if (turn == 0) {
                if (unknown()) {
                    turn = 1;
                } else {
                    turn = 2;
                }
            } else if (turn == 1 && x == y) {
                if (x == y)
                    i = i + 1;
                else {
                    j = j + 1;
                }
                if (unknown()) {
                    turn = 1;
                } else {
                    turn = 2;
                }
            } else if (turn == 2 && i >= j) {
                if (i >= j)
                    x = x + 1;
                y = y + 1;
                turn = 0;
            }
        }

        assert(i >= j);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}