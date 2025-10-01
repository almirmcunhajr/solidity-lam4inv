// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int i, int j) {
        i = 0;
        j = 0;
        x = 0;
        y = 0;

        while (unknown()) {
            i = i + x + 1;
            if (unknown()) {
                j = j + y + 1;
            } else {
                j = j + y + 2;
            }
            x = x + 1;
            y = y + 1;
        }

        assert(j >= i);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}