// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        x = 1;
        y = 1;

        while (y > 0) {
            if (x < 50) {
                y++;
            } else {
                y--;
            }
            x = x + 1;
        }

        assert(x == 100);
    }

    function unknown() internal view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}