// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int n, int i, int j) {
        i = 0;
        j = 0;
        require(n <= 50000001, "failed pre-condition");
        while (i < n) {
            if (unknown()) {
                i = i + 6;
            } else {
                i = i + 3;
            }
        }
        assert(i % 3 == 0);
    }

    function unknown() private view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}