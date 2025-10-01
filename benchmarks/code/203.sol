// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y) {
        require(x <= 1, "failed pre-condition");
        require(x >= 0, "failed pre-condition");
        y = -3;
        while (unknown()) {
            if (x - y < 2) {
                x = x - 1;
                y = y + 2;
            } else if (x - y >= 2) {
                y = y + 1;
            }
        }
        assert(x <= 1);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}