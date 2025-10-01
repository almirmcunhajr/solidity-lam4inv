// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j, int x, int y) {
        i = x;
        j = y;
        while (x != 0) {
            x = x - 1;
            y = y - 1;
        }
        if (y != 0) {
            assert(i != j);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}