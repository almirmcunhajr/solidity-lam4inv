// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int n) {
        require(x >= 0, "failed pre-condition");
        require(x <= y, "failed pre-condition");
        require(y < n, "failed pre-condition");

        while (x < n) {
            x = x + 1;
            if (x > y) {
                y = y + 1;
            }
        }

        assert(y == n);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}