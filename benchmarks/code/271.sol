// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int t) {
        y = t;
        require(x != y, "failed pre-condition");
        while (unknown()) {
            if (x > 0) {
                y = y + x;
            }
        }
        assert(y >= t);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}