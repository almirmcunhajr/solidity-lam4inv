// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int j, int k, int t) {
        j = 2;
        k = 0;

        while (unknown()) {
            if (t == 0) {
                j = j + 4;
            } else {
                j = j + 2;
                k = k + 1;
            }
        }

        if (k != 0) {
            assert(t != 0 && j == k * 2 + 2);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
        }
}