// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int n, int x) {
        x = n;
        while (x > 1) {
            x = x - 1;
        }
        if (x != 1) {
            assert(n <= 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}