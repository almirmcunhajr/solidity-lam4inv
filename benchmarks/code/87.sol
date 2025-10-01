// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int lock, int x, int y) {
        x = y;
        lock = 1;
        while (x != y) {
            if (unknown()) {
                lock = 1;
                x = y;
            } else {
                lock = 0;
                x = y;
                y = y + 1;
            }
        }
        assert(lock == 1);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}