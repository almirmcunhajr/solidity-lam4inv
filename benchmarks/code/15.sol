// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int m, int n) {
        x = 0;
        m = 0;

        while (x < n) {
            if (unknown()) {
                m = x;
            }
            x = x + 1;
        }

        if (n > 0) {
            assert(m < n);
        }
    }

    function unknown() internal view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}