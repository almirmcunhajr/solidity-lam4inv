// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int x, int y) {
        i = 0;
        require(x >= 0, "failed pre-condition");
        require(y >= 0, "failed pre-condition");
        require(x >= y, "failed pre-condition");
        while (unknown()) {
            if (i < y) {
                i = i + 1;
            }
        }
        if (i < y) {
            assert(i < x);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}