// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int x) {
        x = 0;
        while (x < 6) {
            x = x + 1;
        }
        assert(x == 6);
    }

    function unknown() private view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}