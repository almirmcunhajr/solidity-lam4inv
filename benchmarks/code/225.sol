// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x) {
        x = 1;
        while (unknown()) {
            x = x + 2;
        }
        assert(x % 2 == 1);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}