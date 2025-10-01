// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x) {
        require(x <= -2, "failed pre-condition");
        require(x >= -3, "failed pre-condition");
        while (unknown()) {
            if (x < 1) {
                x = x + 2;
            } else if (x >= 1) {
                x = x + 1;
            }
        }
        assert(x >= -5);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}