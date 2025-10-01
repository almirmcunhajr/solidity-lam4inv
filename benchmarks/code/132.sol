// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j, int c, int t) {
        i = 0;

        while (unknown()) {
            if (c > 48) {
                if (c < 57) {
                    j = i + i;
                    t = c - 48;
                    i = j + t;
                }
            }
        }

        assert(i >= 0);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}