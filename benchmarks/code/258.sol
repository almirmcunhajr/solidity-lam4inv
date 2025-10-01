// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x) {
        x = 0;
        while (unknown()) {
            if (unknown()) {
                x = x + 1;
                if (x > 40) {
                    x = 0;
                }
            }
        }
        assert(x >= 0);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}