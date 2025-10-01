// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int x, int y) {
        i = 0;
        require(x >= 0, "failed pre-condition");
        require(y >= 0, "failed pre-condition");
        require(x >= y, "failed pre-condition");
        while (unknown()) {
            if (i < y) {
                i = i + 1;
            }
        }
        if (i < y) {
            assert(0 <= i);
        }
    }

    function unknown() private view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}