// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j, int x, int y) {
        j = 0;
        i = 0;
        y = 2;
        while (i <= x) {
            i = i + 1;
            j = j + y;
        }
        if (y == 1) {
            assert(i == j);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}