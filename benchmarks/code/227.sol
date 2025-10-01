// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y) {
        x = 0;
        while (x < 99) {
            if (y % 2 == 0) {
                x += 10;
            } else {
                x -= 5;
            }
        }
        assert((x % 2) == (y % 2));
    }

    function unknown() external view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}