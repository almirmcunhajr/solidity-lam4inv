// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

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
        if (y == 0) {
            assert(x != 4);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}