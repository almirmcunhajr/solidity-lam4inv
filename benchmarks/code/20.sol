// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int m, int n) {
        x = 0;
        m = 0;

        while (x < n) {
            if (unknown()) {
                m = x;
            }
            x = x + 1;
        }

        if (n > 0) {
            assert(m >= 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}