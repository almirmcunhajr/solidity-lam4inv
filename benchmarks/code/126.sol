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
        if (i == j) {
            assert(y == 0);
        }
    }

    function unknown() public view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}