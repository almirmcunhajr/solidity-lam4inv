// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y) {
        require(x >= 0, "failed pre-condition");
        require(x <= 2, "failed pre-condition");
        require(y <= 2, "failed pre-condition");
        require(y >= 0, "failed pre-condition");
        while (unknown()) {
            x = x + 2;
            y = y + 2;
        }
        if (x == 4) {
            assert(y != 0);
        }
    }

    function unknown() private view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}