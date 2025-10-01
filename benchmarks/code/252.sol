// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int i, int j, int a, int b) {
        a = 0;
        b = 0;
        j = 1;
        i = 0;

        while (unknown()) {
            a = a + 1;
            b = b + j - i;
            i = i + 2;
            if (i % 2 == 0) {
                j = j + 2;
            } else {
                j = j + 1;
            }
        }

        assert(a == b);
    }

    function unknown() private view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}