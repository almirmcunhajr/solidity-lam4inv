// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int c) {
        c = 0;
        while (unknown()) {
            if (unknown()) {
                if (c != 4) {
                    c = c + 1;
                }
            } else {
                if (c == 4) {
                    c = 1;
                }
            }
        }
        if (c != 4) {
            assert(c <= 4);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}