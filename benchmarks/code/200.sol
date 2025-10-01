// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x1, int x2, int x3, int d1, int d2, int d3) {
        d1 = 1;
        d2 = 1;
        d2 = 1;

        while (x1 > 0 && x2 > 0 && x3 > 0) {
            if (unknown()) {
                x1 = x1 - d1;
            }
            if (unknown()) {
                x2 = x2 - d2;
            }
            if (unknown()) {
                x3 = x3 - d3;
            }
        }

        assert(x1 < 0 || x2 < 0 || x3 < 0 || x1 == 0 || x2 == 0 || x3 == 0);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}