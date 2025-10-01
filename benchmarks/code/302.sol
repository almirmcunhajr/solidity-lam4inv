// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j) {
        i = 0;

        while (i < 50000001) {
            if (unknown()) {
                i = i + 8;
            } else {
                i = i + 4;
            }
        }

        if (j == (i / 4)) {
            assert((j * 4) == i);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}