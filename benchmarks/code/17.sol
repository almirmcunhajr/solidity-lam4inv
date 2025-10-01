// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int x, int m, int n) {
        x = 1;
        m = 1;

        while (x < n) {
            if (unknown()) {
                m = x;
            }
            x = x + 1;
        }

        if (n > 1) {
            assert(m < n);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}