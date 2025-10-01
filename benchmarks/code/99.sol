// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int n, int x, int y) {
        require(n >= 0, "failed pre-condition");
        x = n;
        y = 0;
        while (x > 0) {
            y = y + 1;
            x = x - 1;
        }
        assert(n == x + y);
    }

    function unknown() public view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}