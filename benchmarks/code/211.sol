// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int z) {
        x = 0;
        y = 0;
        z = 0;

        while (unknown()) {
            x = x + 1;
            y = y + 2;
            z = z + 3;
        }

        assert(z >= 0);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}