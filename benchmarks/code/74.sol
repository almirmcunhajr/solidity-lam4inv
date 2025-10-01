// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int c, int y, int z) {
        c = 0;
        require(y >= 0, "failed pre-condition");
        require(y <= 127, "failed pre-condition");
        z = (36 * y);
        while (unknown()) {
            if (c < 36) {
                z = (z + 1);
                c = (c + 1);
            }
        }
        if (c < 36) {
            assert(z >= 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}