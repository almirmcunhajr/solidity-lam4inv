// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(uint x) {
        x = 0;
        while (x < 100000000) {
            if (x < 10000000) {
                x++;
            } else {
                x += 2;
            }
        }
        assert(x == 100000000);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}