// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int n, int x, int y) {
        x = 1;

        while (x <= n) {
            y = n - x;
            x = x + 1;
        }

        if (n > 0) {
            assert(y >= 0);
        }
    }

    function unknown() public view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}